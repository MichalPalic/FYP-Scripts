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
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/characterisation/{specname}_r_eff_seq_dist.png}}
                \\caption{{\small Store->load pairs by commit distance}}
            \\end{{subfigure}}
            \\hfill
            \\begin{{subfigure}}[b]{{0.49\\textwidth}}
                \\centering
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/characterisation/{specname}_r_branch_dist.png}}
                \\caption{{\small Store->load pairs by separating branches}}
            \\end{{subfigure}}
            \\begin{{subfigure}}[b]{{0.49\\textwidth}}
                \\centering
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/characterisation/{specname}_r_mdp_takenness.png}}
                \\caption{{\small Store->load pair takenness}}
            \\end{{subfigure}}
            \\hfill
            \\begin{{subfigure}}[b]{{0.49\\textwidth}}
                \\centering
                \\includegraphics[width=\\textwidth]{{appendix/figures/figures/characterisation/{specname}_r_path_dist.png}}
                \\caption{{\small Store->load pairs by path count}}
            \\end{{subfigure}}

                \\caption{{{specname} memory dependence metrics estimate}}
        \\end{{figure}}
    """
    )