"""Faithful, line-by-line transcription of every recipe dict defined in
2025_injection.ipynb (cells 1-41; cells 38 and 42 were empty and are skipped).

Each plasmid line carries EXPLICIT separate fields (construct_id, inject_amount,
stock_conc, inject_volume, mix_volume_at_calc) rather than being parsed out of the
combined "Name | ID" / "ID | Name" strings, because key ordering is genuinely
inconsistent across cells in the source notebook - positional parsing would be
unsafe. `display_text` preserves the original historical label verbatim for
faithful display/export.

migrate_notebook.py calls the real calculate_injection() live against these
values - nothing here is a pre-computed result.

experiment_date is a best-effort inference: for cells that called
write_experiment(), the literal filename date is used unless flagged otherwise
in migration_note; for preview-only cells (no write_experiment call), the date
is inferred from the cell's variable-name/position in the chronological
sequence and is explicitly not authoritative.
"""

EXPERIMENTS = [
    # ---- Preview-only cells (1-17, 20 [not 20; see below], 21 among the "written"
    #      set) - never called write_experiment() in the original notebook. ----
    {
        "cell_index": 1, "source_label": "jan22", "filename": None,
        "experiment_date": "2025-01-22", "date_inferred": True,
        "mixes": {
            "jan22a": {"lines": [
                {"kind": "plasmid", "construct_id": "F126", "display_text": "dpaGFP.nos3'UTR | F126",
                 "inject_amount": 80, "stock_conc": 709},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "cxcr4bTMD-GFP-2xMS2.nos3'UTR | F368",
                 "inject_amount": 100, "stock_conc": 638.0},
                {"kind": "reagent", "display_text": "Nanos MO | #244", "manual_volume": 0.6},
            ]},
            "jan22b": {"lines": [
                {"kind": "plasmid", "construct_id": "D545", "display_text": "mCherry-nanos.nos3'UTR-24xMS2 | D545",
                 "inject_amount": 150, "stock_conc": 1337.5},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "cxcr4bTMD-GFP-2xMS2.nos3'UTR | F368",
                 "inject_amount": 100, "stock_conc": 638.0},
                {"kind": "reagent", "display_text": "Nanos MO | #244", "manual_volume": 0.6},
            ]},
            "jan22c": {"lines": [
                {"kind": "plasmid", "construct_id": "D545", "display_text": "mCherry-nanos.nos3'UTR-24xMS2 | D545",
                 "inject_amount": 150, "stock_conc": 1337.5},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "cxcr4bTMD-GFP-2xMS2.nos3'UTR | F368",
                 "inject_amount": 100, "stock_conc": 638.0},
                {"kind": "reagent", "display_text": "Control MO | #1", "manual_volume": 0.6},
            ]},
        },
    },
    {
        "cell_index": 2, "source_label": "jan28", "filename": None,
        "experiment_date": "2025-01-28", "date_inferred": True,
        "mixes": {
            "jan28": {"lines": [
                {"kind": "plasmid", "construct_id": "F339", "display_text": "mScarlet-Tdrd7a.nos3'UTR | F339",
                 "inject_amount": 150, "stock_conc": 1622.5},
                {"kind": "plasmid", "construct_id": "291", "display_text": "vasa-GFP-vasa.vasa3'UTR | 291",
                 "inject_amount": 100, "stock_conc": 1553.6},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 120, "stock_conc": 824.4},
                {"kind": "reagent", "display_text": "Cxcr4b MO | #12", "manual_volume": 0.6},
            ]},
        },
    },
    {
        "cell_index": 3, "source_label": "jan30", "filename": None,
        "experiment_date": "2025-01-30", "date_inferred": True,
        "mixes": {
            "jan30a": {"lines": [
                {"kind": "plasmid", "construct_id": "F263", "display_text": "gra-mScarlet.globin | F263",
                 "inject_amount": 80, "stock_conc": 1599.3},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 240.4},
                {"kind": "reagent", "display_text": "Conversion Mix 66% | ", "manual_volume": 1.164},
            ]},
            "jan30b": {"lines": [
                {"kind": "plasmid", "construct_id": "F263", "display_text": "gra-mScarlet.globin | F263",
                 "inject_amount": 80, "stock_conc": 1599.3},
                {"kind": "plasmid", "construct_id": "F340", "display_text": "kif5a-GFP-tdrd7a.nos | F340",
                 "inject_amount": 125, "stock_conc": 399.3},
                {"kind": "reagent", "display_text": "Conversion Mix 66% | ", "manual_volume": 1.164},
            ]},
        },
    },
    {
        "cell_index": 4, "source_label": "feb26", "filename": None,
        "experiment_date": "2025-02-26", "date_inferred": True,
        "mixes": {
            "feb26": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 240.4},
                {"kind": "plasmid", "construct_id": "D378", "display_text": "mCherry-nanos.globin | D378",
                 "inject_amount": 80, "stock_conc": 634.2},
            ]},
        },
    },
    {
        "cell_index": 5, "source_label": "mar06", "filename": None,
        "experiment_date": "2025-03-06", "date_inferred": True,
        "mixes": {
            "mar06a": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "A389", "display_text": "EGFP-tdrd7a.nos3'UTR | A389",
                 "inject_amount": 155, "stock_conc": 857.1},
                {"kind": "plasmid", "construct_id": "D211", "display_text": "DCP2-mCherry.globin3'UTR | D211",
                 "inject_amount": 100, "stock_conc": 930.3},
                {"kind": "reagent", "display_text": "Cxcr4b MO | #12", "manual_volume": 0.6},
            ]},
            "mar06b": {"lines": [
                {"kind": "plasmid", "construct_id": "291", "display_text": "vasa-GFP-vasa.vasa3'UTR | 291",
                 "inject_amount": 100, "stock_conc": 1553.6},
                {"kind": "plasmid", "construct_id": "D211", "display_text": "DCP2-mCherry.globin3'UTR | D211",
                 "inject_amount": 100, "stock_conc": 930.3},
                {"kind": "reagent", "display_text": "Cxcr4b MO | #12", "manual_volume": 0.6},
            ]},
        },
    },
    {
        "cell_index": 6, "source_label": "mar11", "filename": None,
        "experiment_date": "2025-03-11", "date_inferred": True,
        "mixes": {
            "mar11": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "D378", "display_text": "mCherry-nanos.globin | D378",
                 "inject_amount": 80, "stock_conc": 634.2},
                {"kind": "reagent", "display_text": "Conversion Mix | 66%", "manual_volume": 1.164},
            ]},
        },
    },
    {
        "cell_index": 7, "source_label": "mar27", "filename": None,
        "experiment_date": "2025-03-27", "date_inferred": True,
        "mixes": {
            "mar27": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "E387", "display_text": "mCherry-nanos.nos3'UTR | E387",
                 "inject_amount": 80, "stock_conc": 845.5},
            ]},
        },
    },
    {
        "cell_index": 8, "source_label": "apr07", "filename": None,
        "experiment_date": "2025-04-07", "date_inferred": True,
        "mixes": {
            "apr07": {"lines": [
                {"kind": "plasmid", "construct_id": "E513", "display_text": "dnd1-mscarletI.nos3'UTR | E513",
                 "inject_amount": 80, "stock_conc": 557.5},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
            ]},
        },
    },
    {
        "cell_index": 9, "source_label": "apr22", "filename": None,
        "experiment_date": "2025-04-22", "date_inferred": True,
        "mixes": {
            "apr22a": {"lines": [
                {"kind": "reagent", "display_text": "Tdrd7a MO | #27", "manual_volume": 0.6},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "E387", "display_text": "mCherry-nanos.nos3'UTR | E387",
                 "inject_amount": 80, "stock_conc": 845.5},
            ]},
            "apr22b": {"lines": [
                {"kind": "reagent", "display_text": "Tdrd7a MO | #27", "manual_volume": 0.6},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F126", "display_text": "dpaGFP.nos3'UTR | F126",
                 "inject_amount": 80, "stock_conc": 709},
                {"kind": "plasmid", "construct_id": "E387", "display_text": "mCherry-nanos.nos3'UTR | E387",
                 "inject_amount": 80, "stock_conc": 845.5},
            ]},
        },
    },
    {
        "cell_index": 10, "source_label": "apr29", "filename": None,
        "experiment_date": "2025-04-29", "date_inferred": True,
        "mixes": {
            "apr29": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "A389", "display_text": "GFP-tdrd7a.nos3'UTR | A389",
                 "inject_amount": 155, "stock_conc": 857.1},
            ]},
        },
    },
    {
        "cell_index": 11, "source_label": "may06", "filename": None,
        "experiment_date": "2025-05-06", "date_inferred": True,
        "mixes": {
            "may06a": {"lines": [
                {"kind": "plasmid", "construct_id": "D211", "display_text": "DCP2-mCherry.globin3'UTR | D211",
                 "inject_amount": 100, "stock_conc": 811.72},
                {"kind": "plasmid", "construct_id": "F247", "display_text": "gra-gfp.globin | F247",
                 "inject_amount": 80, "stock_conc": 1972.3},
                {"kind": "reagent", "display_text": "conversion mix w/ Tdrd7a | 66%", "manual_volume": 1.164},
            ]},
            "may06b": {"lines": [
                {"kind": "plasmid", "construct_id": "D211", "display_text": "DCP2-mCherry.globin3'UTR | D211",
                 "inject_amount": 100, "stock_conc": 811.72},
                {"kind": "plasmid", "construct_id": "F247", "display_text": "gra-gfp.globin | F247",
                 "inject_amount": 80, "stock_conc": 1972.3},
                {"kind": "reagent", "display_text": "conversion mix w/o Tdrd7a| 66%", "manual_volume": 1.164},
            ]},
        },
    },
    {
        "cell_index": 12, "source_label": "jun4", "filename": None,
        "experiment_date": "2025-06-04", "date_inferred": True,
        "mixes": {
            "jun4a": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "F063", "display_text": "mCherry-dnd1.globin | F063",
                 "inject_amount": 80, "stock_conc": 1624.4},
                {"kind": "reagent", "display_text": "Conversion Mix | 66%", "manual_volume": 1.164},
            ]},
            "jun4b": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F063", "display_text": "mCherry-dnd1.globin | F063",
                 "inject_amount": 80, "stock_conc": 1624.4},
                {"kind": "reagent", "display_text": "Conversion Mix | 66%", "manual_volume": 1.164},
            ]},
        },
    },
    {
        "cell_index": 13, "source_label": "jun17", "filename": None,
        "experiment_date": "2025-06-17", "date_inferred": True,
        "mixes": {
            "jun17": {"lines": [
                {"kind": "plasmid", "construct_id": "F162", "display_text": "Dnd1-dendra2.nos3'UTR | F162",
                 "inject_amount": 80, "stock_conc": 1008.3},
            ]},
        },
    },
    {
        "cell_index": 14, "source_label": "jun25", "filename": None,
        "experiment_date": "2025-06-25", "date_inferred": True,
        "mixes": {
            "jun25": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "F063", "display_text": "mCherry-dnd1.globin | F063",
                 "inject_amount": 80, "stock_conc": 1624.4},
                {"kind": "reagent", "display_text": "Tdrd7a MO | MO#27", "manual_volume": 0.5},
            ]},
        },
    },
    {
        "cell_index": 15, "source_label": "jul03", "filename": None,
        "experiment_date": "2025-07-03", "date_inferred": True,
        "mixes": {
            "jul03": {"lines": [
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mcherry-dnd.nos3'UTR | B465",
                 "inject_amount": 100, "stock_conc": 717.2},
                {"kind": "plasmid", "construct_id": "F368", "display_text": "TMD-EGFP-Tdrd7a.nos3'UTR | F368",
                 "inject_amount": 155, "stock_conc": 821.9},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "reagent", "display_text": "Tdrd7a MO | MO#27", "manual_volume": 0.45},
            ]},
        },
    },
    {
        "cell_index": 16, "source_label": "jul23", "filename": None,
        "experiment_date": "2025-07-23", "date_inferred": True,
        "mixes": {
            "jul23a": {"lines": [
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 80, "stock_conc": 824.4},
                {"kind": "plasmid", "construct_id": "291", "display_text": "vasa-GFP-vasa.vasa3'UTR | 291",
                 "inject_amount": 120, "stock_conc": 1553.6},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mcherry-dnd.nos3'UTR | B465",
                 "inject_amount": 100, "stock_conc": 717.2},
                {"kind": "reagent", "display_text": "MO 12 | Cxcr4b MO #12", "manual_volume": 0.6},
                {"kind": "reagent", "display_text": "MO 27 | Tdrd7a MO #27", "manual_volume": 0.45},
            ]},
            "jul23b": {"lines": [
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 80, "stock_conc": 824.4},
                {"kind": "plasmid", "construct_id": "291", "display_text": "vasa-GFP-vasa.vasa3'UTR | 291",
                 "inject_amount": 120, "stock_conc": 1553.6},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mcherry-dnd.nos3'UTR | B465",
                 "inject_amount": 100, "stock_conc": 717.2},
                {"kind": "reagent", "display_text": "MO 12 | Cxcr4b MO #12", "manual_volume": 0.6},
                {"kind": "reagent", "display_text": "MO 1 | Control MO #1", "manual_volume": 0.45},
            ]},
        },
    },
    {
        "cell_index": 17, "source_label": "aug06", "filename": None,
        "experiment_date": "2025-08-06", "date_inferred": True,
        "mixes": {
            "aug06": {"lines": [
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.nos3UTR | F362",
                 "inject_amount": 100, "stock_conc": 150},
                {"kind": "plasmid", "construct_id": "F356", "display_text": "32xALFA-H2A-mcherry.globin3'UTR | F356",
                 "inject_amount": 100, "stock_conc": 300},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
            ]},
        },
    },

    # ---- Cells that called write_experiment() - real historical filenames/dates. ----
    {
        "cell_index": 18, "source_label": "aug08", "filename": "20250808 RNA longevity",
        "experiment_date": "2025-08-08", "date_inferred": False,
        "mixes": {
            "aug08a": {"lines": [
                {"kind": "plasmid", "construct_id": "C946", "display_text": "mCherry.globin3'UTR | C946",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "355", "display_text": "EGFP.nos3'UTR | 355",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "reagent", "display_text": "Conversion Mix + tdrd7a | 66%", "manual_volume": 1.164},
            ]},
            "aug08b": {"lines": [
                {"kind": "plasmid", "construct_id": "C946", "display_text": "mCherry.globin3'UTR | C946",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "355", "display_text": "EGFP.nos3'UTR | 355",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "reagent", "display_text": "Conversion Mix - tdrd7a | 66%", "manual_volume": 1.164},
            ]},
        },
    },
    {
        "cell_index": 19, "source_label": "aug12", "filename": "20250812 RNA longevity",
        "experiment_date": "2025-08-12", "date_inferred": False,
        "mixes": {
            "aug12a": {"lines": [
                {"kind": "plasmid", "construct_id": "B289", "display_text": "GFP.globin3'UTR | B289",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "C947", "display_text": "mCherry.nos3'UTR | C947",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "reagent", "display_text": "Conversion Mix + tdrd7a | 66%", "manual_volume": 1.164},
            ]},
            "aug12b": {"lines": [
                {"kind": "plasmid", "construct_id": "B289", "display_text": "GFP.globin3'UTR | B289",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "C947", "display_text": "mCherry.nos3'UTR | C947",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
                {"kind": "reagent", "display_text": "Conversion Mix - tdrd7a | 66%", "manual_volume": 1.164},
            ]},
            "aug12c": {"lines": [
                {"kind": "reagent", "display_text": "MO #12 | cxcl12a MO #12", "manual_volume": 0.3},
            ]},
        },
    },
    {
        "cell_index": 20, "source_label": "sep22", "filename": "20250923_dnd1_gra_vasa",
        "experiment_date": "2025-09-23", "date_inferred": False,
        "migration_note": "Notebook variable name is 'sep22' but the historical filename this "
                           "was written to is dated 20250923 (Sep 23) - a real mismatch in the "
                           "source notebook between variable name and saved date, preserved here "
                           "rather than guessed at; experiment_date follows the filename (what was "
                           "actually saved to disk).",
        "mixes": {
            "sep22": {"lines": [
                {"kind": "plasmid", "construct_id": "F063", "display_text": "mCherry-dnd1.globin | F063",
                 "inject_amount": 80, "stock_conc": 1624.4},
                {"kind": "plasmid", "construct_id": "E908", "display_text": "gra-GFP.nos3'UTR | E908",
                 "inject_amount": 80, "stock_conc": 1478.5},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
            ]},
        },
    },
    {
        "cell_index": 21, "source_label": "sep23", "filename": "20250923 SunTag confocal live",
        "experiment_date": "2025-09-23", "date_inferred": False,
        "mixes": {
            "sep23a": {"lines": [
                {"kind": "plasmid", "construct_id": "F346", "display_text": "scFv-msGFP2-GB1-NLS.nos3UTR | F346",
                 "inject_amount": 100, "stock_conc": 311.2},
                {"kind": "plasmid", "construct_id": "F347", "display_text": "20xGCN4-H2A-mCherry.nos 3´UTR | F347",
                 "inject_amount": 100, "stock_conc": 628.7},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
            ]},
            "sep23b": {"lines": [
                {"kind": "plasmid", "construct_id": "F346", "display_text": "scFv-msGFP2-GB1-NLS.nos3UTR | F346",
                 "inject_amount": 100, "stock_conc": 311.2},
                {"kind": "plasmid", "construct_id": "F126", "display_text": "dpaGFP.nos3'UTR | F126",
                 "inject_amount": 100, "stock_conc": 709},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 1436.7},
            ]},
        },
    },
    {
        "cell_index": 22, "source_label": "oct13", "filename": "20251013_morphants_dnd1_tdrd7a",
        "experiment_date": "2025-10-13", "date_inferred": False,
        "mixes": {
            "oct13a": {"lines": [
                {"kind": "reagent", "display_text": "MO12 | cxcl12a MO #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "MO1 | control MO #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "F115 | tagBFP-nls.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 586},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "B465 | mcherry-dnd.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 952, "inject_volume": 6,
                 "review_note": "Source explicitly passed inject_volume=6 (3rd positional arg to "
                                 "calculate_injection), overriding the default of 2; identical override "
                                 "used in oct13a/b/c. Because this falls into calculate_injection's "
                                 "auto-dilution branch, the historical injection.py bug applies: the "
                                 "dilution retry loop (func(inject_amount, stock_conc/dil_fac)) ignores "
                                 "the caller's inject_volume/mix_volume and always uses the func() "
                                 "defaults (iv=2, mv=3) regardless. Migrated faithfully as originally "
                                 "computed, not 'corrected'."},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "F125 | dpaGFP.nos3'UTR",
                 "inject_amount": 200, "stock_conc": 1446},
            ]},
            "oct13b": {"lines": [
                {"kind": "reagent", "display_text": "MO12 | cxcl12a MO #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "MO27 | tdrd7a MO #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "F115 | tagBFP-nls.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 586},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "B465 | mcherry-dnd.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 952, "inject_volume": 6,
                 "review_note": "Source explicitly passed inject_volume=6 (3rd positional arg); "
                                 "see oct13a's B465 line for the full note on the dilution-loop bug."},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "F125 | dpaGFP.nos3'UTR",
                 "inject_amount": 200, "stock_conc": 1446},
            ]},
            "oct13c": {"lines": [
                {"kind": "reagent", "display_text": "MO12 | cxcl12a MO #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "MO27 | tdrd7a MO #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "F115 | tagBFP-nls.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 586},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "B465 | mcherry-dnd.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 952, "inject_volume": 6,
                 "review_note": "Source explicitly passed inject_volume=6 (3rd positional arg); "
                                 "see oct13a's B465 line for the full note on the dilution-loop bug."},
                {"kind": "plasmid", "construct_id": "F458", "display_text": "F458 | TMD-tdrd7a.nos3'UTR",
                 "inject_amount": 200, "stock_conc": 900,
                 "review_note": "plasmid_db.csv records F458 as 'mCherry.GlobinUTR', but the notebook "
                                 "uses it here as 'TMD-tdrd7a.nos3'UTR' - naming mismatch, verify which "
                                 "is correct before trusting either label."},
            ]},
        },
    },
    {
        "cell_index": 23, "source_label": "oct23", "filename": "20251023 CaAR reaction in zebrafish – trial 1",
        "experiment_date": "2025-10-23", "date_inferred": False,
        "mixes": {
            "oct23": {"lines": [
                {"kind": "plasmid", "construct_id": "B852", "display_text": "lifeact-Ruby.globin3'UTR | B852",
                 "inject_amount": 100, "stock_conc": 2000},
            ]},
        },
    },
    {
        "cell_index": 24, "source_label": "oct27", "filename": "20251027_ALFAtag_repeat2",
        "experiment_date": "2025-10-27", "date_inferred": False,
        "mixes": {
            "oct27a": {"lines": [
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.nos3UTR | F362",
                 "inject_amount": 50, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F356", "display_text": "32xALFA-H2A-mcherry.globin3'UTR | F356",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "oct27b": {"lines": [
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.nos3UTR | F362",
                 "inject_amount": 50, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F126", "display_text": "dpaGFP.nos3'UTR | F126",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 25, "source_label": "oct29", "filename": "20251029 tdrd7a morphants timeseries",
        "experiment_date": "2025-10-29", "date_inferred": False,
        "mixes": {
            "oct29a": {"lines": [
                {"kind": "reagent", "display_text": "MO12 | cxcl12a MO #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "MO1 | control MO #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "F115 | tagBFP-nls.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "B465 | mcherry-dnd.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "F125 | dpaGFP.nos3'UTR",
                 "inject_amount": 300, "stock_conc": 750},
            ]},
            "oct29b": {"lines": [
                {"kind": "reagent", "display_text": "MO12 | cxcl12a MO #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "MO27 | tdrd7a MO #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "F115 | tagBFP-nls.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "B465 | mcherry-dnd.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "F125 | dpaGFP.nos3'UTR",
                 "inject_amount": 300, "stock_conc": 750},
            ]},
            "oct29c": {"lines": [
                {"kind": "reagent", "display_text": "MO12 | cxcl12a MO #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "MO27 | tdrd7a MO #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "F115 | tagBFP-nls.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "B465 | mcherry-dnd.nos3'UTR",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F458", "display_text": "F458 | TMD-tdrd7a.nos3'UTR",
                 "inject_amount": 300, "stock_conc": 1000,
                 "review_note": "plasmid_db.csv records F458 as 'mCherry.GlobinUTR', but the notebook "
                                 "uses it here as 'TMD-tdrd7a.nos3'UTR' - naming mismatch, verify which "
                                 "is correct before trusting either label."},
            ]},
        },
    },
    {
        "cell_index": 26, "source_label": "nov18", "filename": "20251118 granule time series (fixation)",
        "experiment_date": "2025-11-18", "date_inferred": False,
        "mixes": {
            "nov18a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "control MO | #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E178", "display_text": "eYFP-NLS.nos3'UTR | E178",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "nov18b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E178", "display_text": "eYFP-NLS.nos3'UTR | E178",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "nov18c": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F458", "display_text": "TMD-tdrd7a.nos3'UTR | F458",
                 "inject_amount": 200, "stock_conc": 500,
                 "review_note": "plasmid_db.csv records F458 as 'mCherry.GlobinUTR', but the notebook "
                                 "uses it here as 'TMD-tdrd7a.nos3'UTR' - naming mismatch, verify which "
                                 "is correct before trusting either label."},
                {"kind": "plasmid", "construct_id": "E178", "display_text": "eYFP-NLS.nos3'UTR | E178",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 27, "source_label": "jan27", "filename": "20260127 granule time series (fixation)",
        "experiment_date": "2026-01-27", "date_inferred": False,
        "mixes": {
            "jan27a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "control MO | #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 80, "stock_conc": 500},
            ]},
            "jan27b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 80, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 28, "source_label": "an28", "filename": "20260128_time_fixations",
        "experiment_date": "2026-01-28", "date_inferred": False,
        "migration_note": "Notebook variable names were 'an28a'/'an28b' (likely a typo for "
                           "'jan28a'/'jan28b'); transcribed verbatim, not renamed.",
        "mixes": {
            "an28a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "control MO | #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "E122", "display_text": "mScarletI.nls | E122",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "an28b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "E122", "display_text": "mScarletI.nls | E122",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 29, "source_label": "arch10", "filename": "20260310_ALFAtag_high",
        "experiment_date": "2026-03-10", "date_inferred": False,
        "mixes": {
            "arch10a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F359", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F359",
                 "inject_amount": 300, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F356", "display_text": "32xALFA-H2A-mcherry.globin3'UTR | F356",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "arch10b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F359", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F359",
                 "inject_amount": 300, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 30, "source_label": "arch24", "filename": "20260324 8hpf and 24hpf Dnd and Gra size quantification",
        "experiment_date": "2026-03-24", "date_inferred": False,
        "migration_note": "Cell 30 called write_experiment() twice against two different filenames "
                           "(this one, override=True, and '20260324 Duolink test injection' below) - "
                           "modeled as two separate experiments sharing the same source cell.",
        "mixes": {
            "arch24a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "control MO | #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "B008", "display_text": "Dnd-GFP.glob | B008",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F263", "display_text": "gra-mScarlet.glob | F263",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "arch24b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "B008", "display_text": "Dnd-GFP.glob | B008",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F263", "display_text": "gra-mScarlet.glob | F263",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 30, "source_label": "arch24", "filename": "20260324 Duolink test injection",
        "experiment_date": "2026-03-24", "date_inferred": False,
        "migration_note": "Second of two write_experiment() calls in cell 30 - see "
                           "'20260324 8hpf and 24hpf Dnd and Gra size quantification' for the other.",
        "mixes": {
            "arch24c": {"lines": [
                {"kind": "plasmid", "construct_id": "E908", "display_text": "gra-GFP.nos3'UTR | E908",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 31, "source_label": "arch31", "filename": "20260331 8hpf and 24hpf Dnd and Gra size quantification",
        "experiment_date": "2026-03-31", "date_inferred": False,
        "mixes": {
            "arch31a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "control MO | #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mCherry-dnd1.nos | B465",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E908", "display_text": "gra-eGFP.nos3'UTR | E908",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "arch31b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mCherry-dnd1.nos | B465",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E908", "display_text": "gra-eGFP.nos3'UTR | E908",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 32, "source_label": "arch31_reuse", "filename": "20260409 10hpf and 24hpf Dnd and Gra size quantification",
        "experiment_date": "2026-04-09", "date_inferred": False,
        "migration_note": "Cell 32 reused the arch31a/arch31b dicts defined in cell 31 verbatim "
                           "(no new dict definitions) and wrote them to a new dated filename.",
        "mixes": {
            "arch31a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "control MO | #1", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mCherry-dnd1.nos | B465",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E908", "display_text": "gra-eGFP.nos3'UTR | E908",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "arch31b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "reagent", "display_text": "tdrd7a MO | #27", "manual_volume": 0.45},
                {"kind": "plasmid", "construct_id": "B465", "display_text": "mCherry-dnd1.nos | B465",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "E908", "display_text": "gra-eGFP.nos3'UTR | E908",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "tagBFP-nls.nos3'UTR | F115",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 33, "source_label": "apr28", "filename": "20260428 10xHA msGFP2",
        "experiment_date": "2026-04-28", "date_inferred": False,
        "mixes": {
            "apr28a": {"lines": [
                {"kind": "plasmid", "construct_id": "F604", "display_text": "10xHA-mCherry.24xMS2v6-nos3'UTR | F604",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F619", "display_text": "antiHA-FB-msGFP2-GB1-NLS.nos3'UTR | F619",
                 "inject_amount": 400, "stock_conc": 811.7},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa | E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "apr28b": {"lines": [
                {"kind": "plasmid", "construct_id": "F604", "display_text": "10xHA-mCherry.24xMS2v6-nos3'UTR | F604",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F619", "display_text": "antiHA-FB-msGFP2-GB1-NLS.nos3'UTR | F619",
                 "inject_amount": 200, "stock_conc": 811.7},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa | E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "apr28c": {"lines": [
                {"kind": "plasmid", "construct_id": "F604", "display_text": "10xHA-mCherry.24xMS2v6-nos3'UTR | F604",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F100", "display_text": "NLS-HA-2xMCP-1xGFP-eRF3.nos3'UTR | F100",
                 "inject_amount": 400, "stock_conc": 968.5},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa | E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 34, "source_label": "apr30", "filename": "20260428 quick and dirty HA double check",
        "experiment_date": "2026-04-30", "date_inferred": True,
        "migration_note": "Historical filename is dated 20260428, identical to cell 33's date, but "
                           "this cell's variable names (apr30a/apr30b) and its position immediately "
                           "after the apr28 cell strongly suggest it was actually run on Apr 30, 2026 - "
                           "a likely date typo in the original filename. slug preserves the literal "
                           "historical filename; experiment_date reflects the inferred (not certain) "
                           "real date - verify against the actual injection date if it matters.",
        "mixes": {
            "apr30a": {"lines": [
                {"kind": "plasmid", "construct_id": "F208", "display_text": "nanos-HA.globin | F208",
                 "inject_amount": 150, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F619", "display_text": "antiHA-FB-msGFP2-GB1-NLS.nos3'UTR | F619",
                 "inject_amount": 400, "stock_conc": 811.7},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa| E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
            "apr30b": {"lines": [
                {"kind": "plasmid", "construct_id": "F604", "display_text": "10xHA-mCherry.24xMS2v6-nos3'UTR | F604",
                 "inject_amount": 500, "stock_conc": 1060},
                {"kind": "plasmid", "construct_id": "F619", "display_text": "antiHA-FB-msGFP2-GB1-NLS.nos3'UTR | F619",
                 "inject_amount": 400, "stock_conc": 811.7},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa | E569",
                 "inject_amount": 120, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 35, "source_label": "may20", "filename": "20260520 reduced number of ALFA tags F634 test injection",
        "experiment_date": "2026-05-20", "date_inferred": False,
        "mixes": {
            "may20a": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F359", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F359",
                 "inject_amount": 400, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F356", "display_text": "32xALFA-H2A-mcherry.globin3'UTR | F356",
                 "inject_amount": 250, "stock_conc": 500},
            ]},
            "may20b": {"lines": [
                {"kind": "reagent", "display_text": "cxcl12a MO | #12", "manual_volume": 0.3},
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F359", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F359",
                 "inject_amount": 400, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 250, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 36, "source_label": "may26", "filename": "20260526 ALFAtag antibody testing",
        "experiment_date": "2026-05-26", "date_inferred": False,
        "mixes": {
            "may26a": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F362",
                 "inject_amount": 400, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "may26b": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F362",
                 "inject_amount": 400, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 200, "stock_conc": 500},
            ]},
            "may26c": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F362",
                 "inject_amount": 400, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 250, "stock_conc": 500},
            ]},
            "may26d": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F390", "display_text": "eGFP-nls.nos3'UTR | F390",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 150, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 37, "source_label": "may27", "filename": "20260527 ALFAtag antibody testing",
        "experiment_date": "2026-05-27", "date_inferred": False,
        "mixes": {
            "may27a": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "may27b": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 150, "stock_conc": 500},
            ]},
            "may27c": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 200, "stock_conc": 500},
            ]},
            "may27d": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 200, "stock_conc": 500},
            ]},
            "may27e": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F362", "display_text": "NB-ALFA-msGFP2-GB1-NLS.globin3'UTR | F362",
                 "inject_amount": 400, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mcherry.nos3'UTR | F634",
                 "inject_amount": 150, "stock_conc": 500},
            ]},
            "may27f": {"lines": [
                {"kind": "plasmid", "construct_id": "F162", "display_text": "dnd1-dendra2.nos3'UTR | F162",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 39, "source_label": "jun23", "filename": "20260623 TMD-nanos-mCherry test injection",
        "experiment_date": "2026-06-23", "date_inferred": False,
        "mixes": {
            "jun23a": {"lines": [
                {"kind": "plasmid", "construct_id": "F559", "display_text": "TMD-nanos-mCherry.no 3'UTR | F559",
                 "inject_amount": 150, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B008", "display_text": "dnd-GFP.globin3'UTR | B008",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "nls-tagBFP.nos | F115",
                 "inject_amount": 80, "stock_conc": 500},
            ]},
            "jun23b": {"lines": [
                {"kind": "plasmid", "construct_id": "F559", "display_text": "TMD-nanos-mCherry.no 3'UTR | F559",
                 "inject_amount": 150, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 100, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F115", "display_text": "nls-tagBFP.nos | F115",
                 "inject_amount": 80, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 40, "source_label": "jul08", "filename": "20260708 ALFAtag PatA treatment",
        "experiment_date": "2026-07-08", "date_inferred": False,
        "mixes": {
            "jul08a": {"lines": [
                {"kind": "plasmid", "construct_id": "F634", "display_text": "19xALFA-H2A-mCherry.nos3'UTR | F634",
                 "inject_amount": 125, "stock_conc": 500},
            ]},
        },
    },
    {
        "cell_index": 41, "source_label": "jul14", "filename": "20260714 TMD nanos-conversion",
        "experiment_date": "2026-07-14", "date_inferred": False,
        "mixes": {
            "jul14a": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B008", "display_text": "dnd1-GFP.globin3'UTR | B008",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "D378", "display_text": "mcherry-nanos3.globin3'UTR | D378",
                 "inject_amount": 80, "stock_conc": 500},
            ]},
            "jul14b": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B008", "display_text": "dnd1-GFP.globin3'UTR | B008",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F649", "display_text": "TMD-mcherry-nanos3.globin3'UTR | F649",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
            "jul14c": {"lines": [
                {"kind": "plasmid", "construct_id": "E569", "display_text": "vasa-BFP-vasa.vasa3'UTR | E569",
                 "inject_amount": 120, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "B008", "display_text": "dnd1-GFP.globin3'UTR | B008",
                 "inject_amount": 80, "stock_conc": 500},
                {"kind": "plasmid", "construct_id": "F125", "display_text": "paGFP.globin3'UTR | F125",
                 "inject_amount": 100, "stock_conc": 500},
            ]},
        },
    },
]
