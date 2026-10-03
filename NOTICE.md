# Notice: material from World Dynamics

The World2 model was created by Jay W. Forrester and published in his book *World Dynamics* (Cambridge, MA: Wright-Allen Press, 1971; 2nd ed. 1973). Copyright in the book belongs to its rights holders. The MIT license in `LICENSE` covers only the code and documentation written for this project, and does not extend to the material listed below.

This repository reproduces the following from the 2nd edition, for scholarly study and to let readers check the Python translations against the original model:

| File | What it contains |
|---|---|
| `source-code.dyn` | A transcription of Appendix B, "Equations of the World Model": the model's DYNAMO listing |
| `definition-of-terms.md` | A transcription of Appendix C, "Definitions of Terms" |
| `validation/README.md` | Short quotations from Chapter 4, with page numbers, compared against our runs |

The Python files, the diagram in `causal-loop-diagram.md` and the plots in `validation/` are our own work, built from the equations in Appendix B.

Scans of the book's pages are **not** included. The tools in `validation/tools/` regenerate the figure overlays from your own copy of the book; their inputs and outputs stay in the git-ignored folders `validation/book-pages/` and `validation/book-overlays/`.

If you hold rights in *World Dynamics* and have a concern about this material, please open an issue on the repository.
