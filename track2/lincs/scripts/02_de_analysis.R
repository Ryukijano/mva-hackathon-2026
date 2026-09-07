#!/usr/bin/env Rscript
# 02_de_analysis.R
# Differential expression for MVA Track 2 LINCS signatures.
# All expression matrices are expected to be log2 scale.

suppressPackageStartupMessages({
  library(limma)
  library(data.table)
  library(dplyr)
  library(readr)
})

base_dir <- "/mnt/scratch/kcwp264/mva-hackathon-2026/track2/lincs"
data_dir <- file.path(base_dir, "data")
res_dir <- file.path(base_dir, "results")

dir.create(res_dir, recursive = TRUE, showWarnings = FALSE)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
read_expr <- function(f) {
  df <- as.data.frame(fread(f, header = TRUE))
  rownames(df) <- df[[1]]
  df[[1]] <- NULL
  # Strip leading/trailing quotes from column names if present
  cn <- gsub('^"|"$', '', names(df))
  names(df) <- make.names(cn, unique = TRUE)
  as.matrix(df)
}

read_meta <- function(f) {
  df <- read.csv(f, stringsAsFactors = FALSE)
  df$sample <- make.names(df$sample, unique = TRUE)
  df
}

run_limma <- function(expr, meta, group, contrast, covariate = NULL, min_prop = 0.5) {
  # Determine which column of meta matches expression column names
  cn <- colnames(expr)
  candidates <- c("geo_accession", "sample")
  id_col <- NULL
  for (cand in candidates) {
    if (cand %in% names(meta) && length(intersect(cn, meta[[cand]])) > 0) {
      id_col <- cand
      break
    }
  }
  if (is.null(id_col)) {
    stop("No meta column matches expression column names")
  }

  # Keep samples present in both expr and meta
  keep <- intersect(cn, meta[[id_col]])
  if (length(keep) < 2) {
    stop(paste("Only", length(keep), "samples matched for contrast:", contrast))
  }
  expr <- expr[, keep, drop = FALSE]
  meta <- meta[match(keep, meta[[id_col]]), ]

  g <- factor(meta[[group]])
  design <- model.matrix(~ 0 + g)
  colnames(design) <- levels(g)

  if (!is.null(covariate) && covariate %in% names(meta)) {
    cov <- factor(meta[[covariate]])
    design <- model.matrix(~ 0 + g + cov)
    # Make contrast refer to the g-prefixed level columns
    lvl <- levels(g)
    contrast_expr <- contrast
    for (lev in lvl) {
      contrast_expr <- gsub(paste0("\\b", lev, "\\b"), paste0("g", lev), contrast_expr)
    }
    contrast <- contrast_expr
  }

  # Filter lowly expressed / unmeasured features
  expr <- expr[rowMeans(is.finite(expr)) >= 0.9, ]

  fit <- lmFit(expr, design)
  cont <- makeContrasts(contrasts = contrast, levels = design)
  fit2 <- contrasts.fit(fit, cont)
  fit2 <- eBayes(fit2, trend = TRUE)
  top <- topTable(fit2, number = Inf, sort.by = "p", adjust.method = "BH")
  top$gene <- rownames(top)
  top <- top[, c("gene", "logFC", "t", "P.Value", "adj.P.Val"), drop = FALSE]
  list(fit = fit2, degs = top, contrast_name = names(cont))
}

write_signature <- function(degs, name, sizes = c(100, 150, 250), out_dir = data_dir) {
  degs <- degs %>% arrange(P.Value)

  # Prefer FDR-significant genes, then fall back to nominal P < 0.01.
  up_fdr <- degs %>% filter(adj.P.Val < 0.05, logFC > 0)
  dn_fdr <- degs %>% filter(adj.P.Val < 0.05, logFC < 0)
  up_nom <- degs %>% filter(P.Value < 0.01, logFC > 0)
  dn_nom <- degs %>% filter(P.Value < 0.01, logFC < 0)

  up <- if (nrow(up_fdr) >= min(sizes)) up_fdr else up_nom
  dn <- if (nrow(dn_fdr) >= min(sizes)) dn_fdr else dn_nom

  composition <- list()
  for (n in sizes) {
    up_n <- head(up$gene, n)
    dn_n <- head(dn$gene, n)
    # Pad with NAs if fewer than n (script will still run; downstream tools should drop NAs)
    writeLines(up_n, file.path(out_dir, paste0(name, "_up_", n, ".txt")))
    writeLines(dn_n, file.path(out_dir, paste0(name, "_down_", n, ".txt")))

    # Track how many genes in this signature are FDR vs nominal
    up_n_fdr <- sum(up_n %in% up_fdr$gene)
    up_n_nom <- length(up_n) - up_n_fdr
    dn_n_fdr <- sum(dn_n %in% dn_fdr$gene)
    dn_n_nom <- length(dn_n) - dn_n_fdr
    composition[[paste0(name, "_", n)]] <- list(
      signature = name,
      size = n,
      up_fdr = up_n_fdr,
      up_nominal = up_n_nom,
      down_fdr = dn_n_fdr,
      down_nominal = dn_n_nom,
      has_nominal_genes = (up_n_nom > 0 || dn_n_nom > 0)
    )
  }

  write.csv(degs, file.path(out_dir, paste0(name, "_degs.csv")), row.names = FALSE)

  list(
    n_up = nrow(up_fdr),
    n_down = nrow(dn_fdr),
    n_up_nominal = nrow(up_nom),
    n_down_nominal = nrow(dn_nom),
    n_total = nrow(degs),
    composition = composition
  )
}

# -----------------------------------------------------------------------------
# Contrasts
# -----------------------------------------------------------------------------
results <- list()

# GSE22206 human MVA
meta <- read_meta(file.path(data_dir, "GSE22206_meta.csv"))
expr <- read_expr(file.path(data_dir, "GSE22206_expr.csv"))

# All case vs control, tissue as covariate
r <- run_limma(expr, meta, "condition", "case - control", covariate = "tissue")
info <- write_signature(r$degs, "GSE22206_case_v_control")
results[["GSE22206_case_v_control"]] <- info

# LCL only
m <- meta[meta$tissue == "LCL", ]
r <- run_limma(expr, m, "condition", "case - control")
info <- write_signature(r$degs, "GSE22206_LCL_case_v_control")
results[["GSE22206_LCL_case_v_control"]] <- info

# Fibroblast only
m <- meta[meta$tissue == "fibroblast", ]
r <- run_limma(expr, m, "condition", "case - control")
info <- write_signature(r$degs, "GSE22206_fibro_case_v_control")
results[["GSE22206_fibro_case_v_control"]] <- info

# GSE134781 early mouse muscle
meta <- read_meta(file.path(data_dir, "GSE134781_meta.csv"))
expr <- read_expr(file.path(data_dir, "GSE134781_expr.csv"))

# heterozygous L1002P vs WT
m <- meta[meta$condition %in% c("WT", "hetL1002P"), ]
r <- run_limma(expr, m, "condition", "hetL1002P - WT")
info <- write_signature(r$degs, "GSE134781_hetL1002P_v_WT")
results[["GSE134781_hetL1002P_v_WT"]] <- info

# heterozygous X753 vs WT
m <- meta[meta$condition %in% c("WT", "hetX753"), ]
r <- run_limma(expr, m, "condition", "hetX753 - WT")
info <- write_signature(r$degs, "GSE134781_hetX753_v_WT")
results[["GSE134781_hetX753_v_WT"]] <- info

# GSE134780 late mouse muscle and fat
meta <- read_meta(file.path(data_dir, "GSE134780_meta.csv"))
expr <- read_expr(file.path(data_dir, "GSE134780_expr.csv"))

for (tiss in c("gastrocnemius muscle", "fat (IAT)")) {
  m <- meta[meta$tissue == tiss & meta$condition %in% c("WT", "HL1002P"), ]
  r <- run_limma(expr, m, "condition", "HL1002P - WT")
  suffix <- if (tiss == "gastrocnemius muscle") "muscle" else "fat"
  info <- write_signature(r$degs, paste0("GSE134780_HL1002P_v_WT_", suffix))
  results[[paste0("GSE134780_HL1002P_v_WT_", suffix)]] <- info

  m <- meta[meta$tissue == tiss & meta$condition %in% c("WT", "HH"), ]
  r <- run_limma(expr, m, "condition", "HH - WT")
  info <- write_signature(r$degs, paste0("GSE134780_HH_v_WT_", suffix))
  results[[paste0("GSE134780_HH_v_WT_", suffix)]] <- info
}

# GSE247267 small RNA aneuploid vs diploid (feature names are not mRNA; used as secondary)
meta <- read_meta(file.path(data_dir, "GSE247267_meta.csv"))
expr <- read_expr(file.path(data_dir, "GSE247267_expr.csv"))
m <- meta[meta$group %in% c("diploid", "aneuploid"), ]
r <- run_limma(expr, m, "group", "aneuploid - diploid")
info <- write_signature(r$degs, "GSE247267_aneuploid_v_diploid")
results[["GSE247267_aneuploid_v_diploid"]] <- info

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
summary_df <- data.frame(
  signature = names(results),
  n_up = sapply(results, `[[`, "n_up"),
  n_down = sapply(results, `[[`, "n_down"),
  n_total = sapply(results, `[[`, "n_total")
)
print(summary_df)
write.csv(summary_df, file.path(res_dir, "de_summary.csv"), row.names = FALSE)

# Write per-signature/size composition (FDR vs nominal gene counts)
comp_rows <- list()
for (r in results) {
  for (key in names(r$composition)) {
    comp_rows[[length(comp_rows) + 1]] <- r$composition[[key]]
  }
}
if (length(comp_rows) > 0) {
  comp_df <- do.call(rbind, lapply(comp_rows, as.data.frame, stringsAsFactors = FALSE))
  write.csv(comp_df, file.path(res_dir, "signature_composition.csv"), row.names = FALSE)
  cat("\n=== Signature composition (FDR vs nominal) ===\n")
  print(comp_df)
}
