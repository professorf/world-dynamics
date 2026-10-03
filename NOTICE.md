# Notice: material from World Dynamics

The World2 model was created by Jay W. Forrester and published in his book *World Dynamics* (Cambridge, MA: Wright-Allen Press, 1971; 2nd ed. 1973). Copyright in the book belongs to its rights holders. The MIT license in `LICENSE` covers only the code and documentation written for this project, and does not extend to the material listed below.

This repository reproduces the following from the 2nd edition, for scholarly study and to let readers check the Python translations against the original model:

| File | What it contains |
|---|---|
| `source-code.dyn` | A transcription of Appendix B, "Equations of the World Model": the model's DYNAMO listing |
| `definition-of-terms.md` | A transcription of Appendix C, "Definitions of Terms" |
| `validation/README.md` | Short quotations from Chapter 4, with page numbers, compared against our runs |
| `validation/book-overlays/` | Images of the twelve figures in Chapter 4 (pp. 70-91), with their captions, with our model runs drawn over them |

The Python files, the diagram in `causal-loop-diagram.md`, the plots at the top level of `validation/`, and the colored curves and headers in the overlays are our own work, built from the equations in Appendix B. The figures are reproduced in the overlays only so that readers can check our runs against Forrester's published output.

Full-page scans of the book are **not** included. The tools in `validation/tools/` regenerate the overlays from your own copy of the book; the page images they read stay in the git-ignored folder `validation/book-pages/`.

If you hold rights in *World Dynamics* and have a concern about this material, please open an issue on the repository.
