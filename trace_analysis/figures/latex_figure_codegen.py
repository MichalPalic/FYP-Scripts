import os
import sys
import glob

figure_dir = 'trace_analysis/figures/'

figpaths = glob.glob(figure_dir + "*eff_seq_dist.png", recursive=True)
figpaths.sort()

for figpath in figpaths:
    specname = figpath.split('/')[-1].split('_')[0]

    print(
    f"""
        \\begin{{figure}}
             \\centering
            \\begin{{subfigure}}[b]{{0.49\\textwidth}}
                \\centering
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/{specname}_r_eff_seq_dist.png}}
                \\caption{{Distribution of Store->Load pairs as a function of uOP distance}}
            \\end{{subfigure}}
            \\hfill
            \\begin{{subfigure}}[b]{{0.49\\textwidth}}
                \\centering
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/{specname}_r_branch_dist.png}}
                \\caption{{Distribution of Store->Load pairs as a function of number of separating branches}}
            \\end{{subfigure}}

            \\begin{{subfigure}}[b]{{0.49\\textwidth}}
                \\centering
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/{specname}_r_mdp_takenness.png}}
                \\caption{{Distribution of Store->Load pair frequency (Takenness)}}
            \\end{{subfigure}}
                \\caption{{Simpoint aggregate {specname} memory dependence metrics}}
                \\label{{fig:three graphs}}
        \\end{{figure}}
    """
    )