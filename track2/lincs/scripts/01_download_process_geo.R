#!/usr/bin/env Rscript
# 01_download_process_geo.R
# Download and clean GEO datasets for MVA Track 2 LINCS analysis.
# Designed to run inside the mva-hackathon-lincs conda environment.

suppressPackageStartupMessages({
  library(GEOquery)
  library(data.table)
  library(edgeR)
  library(dplyr)
  library(stringr)
  library(readr)
})

base_dir <- "/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs"
data_dir <- file.path(base_dir, "data")
raw_dir <- file.path(data_dir, "raw")
log_dir <- file.path(base_dir, "logs")

dir.create(raw_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)

log_file <- file.path(log_dir, "download_process_geo.log")
logger <- function(...) {
  msg <- paste(format(Sys.time(), "%Y-%m-%d %H:%M:%S"), paste(..., collapse = " "))
  message(msg)
  cat(msg, "\n", file = log_file, append = TRUE)
}

# -----------------------------------------------------------------------------
# Helper: safely download a file via HTTPS/FTP
# -----------------------------------------------------------------------------
safe_download <- function(url, dest, max_tries = 3) {
  for (i in seq_len(max_tries)) {
    tryCatch({
      download.file(url, dest, mode = "wb", method = "auto")
      if (file.exists(dest) && file.size(dest) > 0) return(TRUE)
    }, error = function(e) logger("Download attempt", i, "failed:", conditionMessage(e)))
    Sys.sleep(5)
  }
  return(FALSE)
}

# -----------------------------------------------------------------------------
# GSE22206 -- human MVA fibroblasts / LCLs (Illumina microarray)
# -----------------------------------------------------------------------------
process_gse22206 <- function() {
  logger("Processing GSE22206...")
  gse <- getGEO("GSE22206", GSEMatrix = TRUE, destdir = raw_dir, getGPL = TRUE)
  es <- gse[[1]]

  expr <- as.data.frame(exprs(es))
  expr$ID <- rownames(expr)

  fdat <- as.data.frame(fData(es))
  fdat$ID <- rownames(fdat)

  # Use the platform Symbol column where present; fall back to Entrez -> lookup if missing
  sym_col <- if ("Symbol" %in% names(fdat)) "Symbol" else "ILMN_Gene"
  probe_map <- fdat[, c("ID", sym_col), drop = FALSE]
  names(probe_map) <- c("ID", "symbol")
  probe_map$symbol <- str_trim(probe_map$symbol)
  probe_map$symbol[probe_map$symbol == ""] <- NA

  # Merge and aggregate by symbol (median)
  expr <- merge(expr, probe_map, by = "ID", all.x = TRUE)
  expr <- expr[!is.na(expr$symbol) & expr$symbol != "", ]

  # Aggregating by gene symbol
  expr_ag <- expr %>%
    group_by(symbol) %>%
    summarise(across(where(is.numeric), median, na.rm = TRUE))

  expr_out <- as.data.frame(expr_ag)
  rownames(expr_out) <- expr_out$symbol
  expr_out$symbol <- NULL

  # Ensure log2 scale (values are already log2-normalised from the series matrix)
  vals <- as.matrix(expr_out)
  if (max(vals, na.rm = TRUE) > 100) vals <- log2(vals + 1)
  expr_out <- as.data.frame(vals)

  # Align expression column names with metadata sample names
  pd <- as.data.frame(pData(es))
  pd$sample <- make.names(as.character(pd$title))
  # rename expression columns from GEO accessions to sample names
  sample_idx <- match(colnames(expr_out), pd$geo_accession)
  if (any(is.na(sample_idx))) stop("Could not match all GSE22206 expression columns to metadata")
  colnames(expr_out) <- pd$sample[sample_idx]

  pd$source <- ifelse(grepl("LCL", pd$title, ignore.case = TRUE), "LCL",
                      ifelse(grepl("Fibro", pd$title, ignore.case = TRUE), "fibroblast", NA))
  pd$tissue <- pd$source

  group <- rep(NA, nrow(pd))
  group[grepl("proband", pd$title, ignore.case = TRUE)] <- "case"
  group[grepl("control", pd$title, ignore.case = TRUE)] <- "control"
  group[grepl("relative", pd$title, ignore.case = TRUE)] <- "carrier"
  pd$group <- group
  pd$condition <- pd$group

  meta <- pd[, c("geo_accession", "sample", "condition", "tissue", "source", "group")]
  # Ensure metadata rows are in the same order as expression columns
  meta <- meta[match(colnames(expr_out), meta$sample), ]

  write.csv(meta, file.path(data_dir, "GSE22206_meta.csv"), row.names = FALSE)
  write.csv(expr_out, file.path(data_dir, "GSE22206_expr.csv"))

  n_genes <- nrow(expr_out)
  n_samples <- ncol(expr_out)
  writeLines(c(
    "# GSE22206 summary",
    "",
    paste("- Sample count:", n_samples),
    paste("- Genes measured:", n_genes),
    "- Platform: Illumina humanRef-8 v2.0 expression beadchip (GPL6104)",
    "- Normalisation: GEO-processed / log2-normalised values from series matrix; median per gene symbol",
    paste("- Groups:", paste(table(meta$group), collapse = ", ")),
    "- Issues: Some probe IDs lacked a gene symbol and were dropped."
  ), file.path(data_dir, "GSE22206_summary.md"))

  logger("GSE22206 done:", n_samples, "samples,", n_genes, "genes")
  return(list(meta = meta, expr = expr_out))
}

# -----------------------------------------------------------------------------
# Ortholog map (mouse gene symbol -> human gene symbol)
# -----------------------------------------------------------------------------
build_ortholog_map <- function() {
  logger("Building mouse-to-human one-to-one ortholog map...")
  url <- "http://www.informatics.jax.org/downloads/reports/HMD_HumanPhenotype.rpt"
  dest <- file.path(raw_dir, "HMD_HumanPhenotype.rpt")
  if (!file.exists(dest)) {
    ok <- safe_download(url, dest, max_tries = 5)
    if (!ok) stop("Failed to download MGI HMD_HumanPhenotype.rpt")
  }

  # Columns: HumanSymbol, HumanEntrez, MouseSymbol, MGI, MP...
  hmd <- fread(dest, header = FALSE, fill = TRUE, sep = "\t")
  hmd <- hmd[, 1:4]
  setnames(hmd, c("human_symbol", "human_entrez", "mouse_symbol", "mgi_id"))
  hmd <- hmd[human_symbol != "" & mouse_symbol != "" & !is.na(human_symbol) & !is.na(mouse_symbol)]

  # Keep only pairs that are one-to-one in both directions
  hmd[, mouse_n := .N, by = mouse_symbol]
  hmd[, human_n := .N, by = human_symbol]
  hmd <- hmd[mouse_n == 1 & human_n == 1, .(mouse_symbol, human_symbol)]

  write.csv(hmd, file.path(data_dir, "gene_ortholog_map.csv"), row.names = FALSE)

  writeLines(c(
    "# gene_ortholog_map.csv",
    "",
    paste("- Rows (one-to-one pairs):", nrow(hmd)),
    "- Source: Mouse Genome Informatics (MGI) HMD_HumanPhenotype.rpt",
    paste("  URL:", url),
    "- Date accessed:", as.character(Sys.Date()),
    "- Filter: retained only mouse symbols and human symbols that are reciprocally unique."
  ), file.path(data_dir, "gene_ortholog_map_source.md"))

  logger("Ortholog map done:", nrow(hmd), "one-to-one pairs")
  return(hmd)
}

# -----------------------------------------------------------------------------
# Mouse count processing helper
# -----------------------------------------------------------------------------
process_mouse_counts <- function(acc, url_counts, meta_acc = acc, title_prefix = "") {
  logger("Processing", acc, "...")
  dest <- file.path(raw_dir, basename(url_counts))
  if (!file.exists(dest)) {
    ok <- safe_download(url_counts, dest)
    if (!ok) stop(paste("Failed to download counts for", acc))
  }

  counts <- fread(dest)
  gene_col <- names(counts)[1]
  samples <- names(counts)[-1]

  # Build count matrix
  mat <- as.matrix(counts[, ..samples])
  rownames(mat) <- counts[[gene_col]]

  # TMM + log2-CPM normalisation
  dge <- DGEList(counts = mat)
  dge <- calcNormFactors(dge, method = "TMM")
  cpm_mat <- cpm(dge, log = TRUE)

  # Metadata from GEO
  gse <- getGEO(meta_acc, GSEMatrix = TRUE, destdir = raw_dir)
  es <- gse[[1]]
  pd <- as.data.frame(pData(es))
  pd$sample <- make.names(as.character(pd$title))

  # Tissue / age / genotype from characteristics (pattern-based to handle variable column order)
  char_cols <- grep("^characteristics_ch1", names(pd), value = TRUE)
  chars <- apply(pd[, char_cols, drop = FALSE], 1, function(x) paste(stats::na.omit(x), collapse = "; "))
  pd$tissue <- stringr::str_trim(stringr::str_match(chars, "tissue:\\s*([^;]+)")[, 2])
  pd$age <- stringr::str_trim(stringr::str_match(chars, "age:\\s*([^;]+)")[, 2])
  pd$genotype <- stringr::str_trim(stringr::str_match(chars, "genotype:\\s*([^;]+)")[, 2])

  pd$condition <- pd$genotype
  pd$group <- ifelse(pd$genotype == "WT", "control", "case")

  meta <- pd[, c("geo_accession", "sample", "condition", "tissue", "age", "genotype", "group")]

  # Align expression columns with metadata sample names
  cpm_df <- as.data.frame(cpm_mat)
  cpm_idx <- match(colnames(cpm_df), pd$title)
  if (any(is.na(cpm_idx))) stop(paste("Could not match all", acc, "expression columns to metadata"))
  colnames(cpm_df) <- pd$sample[cpm_idx]
  # Ensure metadata rows match expression column order
  meta <- meta[match(colnames(cpm_df), meta$sample), ]

  # Map to human orthologs
  map <- build_ortholog_map()
  cpm_df$mouse_symbol <- rownames(cpm_df)
  cpm_df <- merge(cpm_df, map, by.x = "mouse_symbol", by.y = "mouse_symbol", all.x = FALSE)
  cpm_df$mouse_symbol <- NULL

  # In case multiple mouse genes map to one human symbol, take the row with highest mean cpm (one-to-one should avoid this)
  sample_cols <- setdiff(names(cpm_df), c("human_symbol"))
  cpm_df$mean_cpm <- rowMeans(cpm_df[, sample_cols, drop = FALSE], na.rm = TRUE)
  cpm_df <- cpm_df %>%
    arrange(desc(mean_cpm)) %>%
    distinct(human_symbol, .keep_all = TRUE) %>%
    select(-mean_cpm)

  rownames(cpm_df) <- cpm_df$human_symbol
  cpm_df$human_symbol <- NULL

  write.csv(meta, file.path(data_dir, paste0(acc, "_meta.csv")), row.names = FALSE)
  write.csv(cpm_df, file.path(data_dir, paste0(acc, "_expr.csv")))

  n_genes <- nrow(cpm_df)
  n_samples <- ncol(cpm_df)
  writeLines(c(
    paste("#", acc, "summary"),
    "",
    paste("- Sample count:", n_samples),
    paste("- Tissue(s):", paste(unique(meta$tissue), collapse = ", ")),
    paste("- Genotype groups:", paste(table(meta$condition), collapse = ", ")),
    "- Platform: RNA-seq",
    "- Normalisation: edgeR TMM + log2-CPM; mapped to one-to-one human orthologs",
    paste("- Human-ortholog genes:", n_genes),
    "- Issues: Mouse genes without a one-to-one human ortholog are excluded."
  ), file.path(data_dir, paste0(acc, "_summary.md")))

  logger(acc, "done:", n_samples, "samples,", n_genes, "human-ortholog genes")
  return(list(meta = meta, expr = cpm_df))
}

# -----------------------------------------------------------------------------
# GSE247267 -- isogenic human aneuploid RPE1 (small RNA / miRNA counts)
# -----------------------------------------------------------------------------
process_gse247267 <- function() {
  logger("Processing GSE247267...")
  url <- "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE247nnn/GSE247267/suppl/GSE247267_raw_counts.txt.gz"
  dest <- file.path(raw_dir, "GSE247267_raw_counts.txt.gz")
  if (!file.exists(dest)) {
    ok <- safe_download(url, dest)
    if (!ok) stop("Failed to download GSE247267 raw counts")
  }

  counts <- fread(dest, fill = TRUE)
  # First column is the feature ID; column name is blank -> V1
  setnames(counts, 1, "feature")
  # Drop any fully-empty trailing columns introduced by inconsistent header/data columns
  empty_cols <- sapply(counts, function(x) all(is.na(x)))
  if (any(empty_cols)) counts <- counts[, which(!empty_cols), with = FALSE]
  samples <- setdiff(names(counts), "feature")

  mat <- as.matrix(counts[, ..samples])
  rownames(mat) <- counts$feature

  # CPM + log2 normalisation
  dge <- DGEList(counts = mat)
  dge <- calcNormFactors(dge, method = "TMM")
  cpm_mat <- cpm(dge, log = TRUE)
  cpm_df <- as.data.frame(cpm_mat)

  # Align expression columns with metadata
  gse <- getGEO("GSE247267", GSEMatrix = TRUE, destdir = raw_dir)
  es <- gse[[1]]
  pd <- as.data.frame(pData(es))
  pd$sample <- make.names(as.character(pd$title))
  cpm_idx <- match(colnames(cpm_df), pd$title)
  if (any(is.na(cpm_idx))) stop("Could not match all GSE247267 expression columns to metadata")
  colnames(cpm_df) <- pd$sample[cpm_idx]

  # Parse characteristics. GSE247267 has dedicated ch1 columns (tissue:, cell line: etc.)
  get_field <- function(nm) {
    col <- if (nm %in% names(pd)) pd[[nm]] else NA
    gsub(paste0("^", nm, ": "), "", col)
  }
  pd$tissue <- get_field("tissue:ch1")
  pd$cell_line <- get_field("cell line:ch1")
  pd$cell_type <- get_field("cell type:ch1")
  pd$genotype <- get_field("genotype:ch1")

  pd$condition <- pd$genotype
  pd$group <- ifelse(grepl("^WT", pd$genotype), "diploid", "aneuploid")
  pd$source <- "RPE1-hTERT"

  meta <- pd[, c("geo_accession", "sample", "condition", "tissue", "cell_line", "cell_type", "genotype", "group", "source")]
  # Ensure metadata rows match expression column order
  meta <- meta[match(colnames(cpm_df), meta$sample), ]

  write.csv(meta, file.path(data_dir, "GSE247267_meta.csv"), row.names = FALSE)
  write.csv(cpm_df, file.path(data_dir, "GSE247267_expr.csv"))

  writeLines(c(
    "# GSE247267 summary",
    "",
    paste("- Sample count:", ncol(cpm_df)),
    paste("- Features measured:", nrow(cpm_df)),
    "- Platform: small RNA-seq (miRNA / isomiR profiling, GPL24676)",
    "- Normalisation: edgeR TMM + log2-CPM",
    paste("- Genotype groups:", paste(table(meta$condition), collapse = ", ")),
    paste("- Broad groups:", paste(table(meta$group), collapse = ", ")),
    "- Issues: This is a non-coding / small-RNA dataset; features are not mRNA gene symbols. The accession requested (GSE247267) is the small-RNA series for the isogenic aneuploid RPE1 system."
  ), file.path(data_dir, "GSE247267_summary.md"))

  logger("GSE247267 done:", ncol(cpm_df), "samples,", nrow(cpm_df), "features")
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
logger("=== Starting GEO download and processing pipeline ===")

tryCatch({
  process_gse22206()
}, error = function(e) {
  logger("GSE22206 FAILED:", conditionMessage(e))
})

tryCatch({
  process_mouse_counts(
    "GSE134781",
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE134nnn/GSE134781/suppl/GSE134781_counts.txt.gz"
  )
}, error = function(e) {
  logger("GSE134781 FAILED:", conditionMessage(e))
})

tryCatch({
  process_mouse_counts(
    "GSE134780",
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE134nnn/GSE134780/suppl/GSE134780_counts.txt.gz"
  )
}, error = function(e) {
  logger("GSE134780 FAILED:", conditionMessage(e))
})

tryCatch({
  process_gse247267()
}, error = function(e) {
  logger("GSE247267 FAILED:", conditionMessage(e))
})

logger("=== Pipeline finished ===")
