from pathlib import Path

def func(ia, sc, iv=2, mv=3):
    vol = ((ia / iv) / sc) * mv
    return vol


def calculate_injection(inject_amount, stock_conc, inject_volume=2, mix_volume=3, name=''):
    dil_fac = 1
    if func(inject_amount, stock_conc, iv=inject_volume, mv=mix_volume) < 0.25:
        # TODO insert a variable for wanted dilution and choose intelligently
        for _ in range(100):
            dil_fac += 1
            final_vol = func(inject_amount, stock_conc / dil_fac)
            if final_vol > 0.25:
                break
    else:
        final_vol = func(inject_amount, stock_conc, iv=inject_volume, mv=mix_volume)

    # print(
        # f'{round(final_vol, 3)} µL of the {dil_fac}x Stock solution should be in the mix. Dilution concentration is {stock_conc / dil_fac} ng/µL')
    return final_vol, stock_conc/dil_fac, inject_amount


def calc_injectionmix(dic, mix_vol=3, phr=True, phr_vol=None):
    if phr_vol is None:
        phr_vol = mix_vol * 0.1  # historical default: 10% of the mix
    total_rna_vol = 0
    output = ['|Name|Construct Number |Volume [µL]| Amount in pg |\n']
    for k, v in dic.items():
        if isinstance(v, float):
            v = (v, 1, 'xx')
            output.append(f'|{k} | ' + f' {round(v[0], 3)}| {v[2]} |\n')
        else:
            output.append(f'|{k} ({v[1]}'+r' $\frac{ng}{µL}$)| '+f' {round(v[0], 3)}| {v[2]} |\n')
        total_rna_vol += v[0]
    if phr:
        total_rna_vol += phr_vol
        output.append(f'|PhR| - |     \t {round(phr_vol, 3)}| - |\n')
    output.append(f'|HEPES| - |    \t {round(mix_vol - total_rna_vol, 3)}| - |\n')
    # for op in output:
    #     print(op, end='')
    return ''.join(output)


def write_experiment(injection_dicts: list, filename: str, override: bool = False):
    path = Path('/Users/julian/Library/Mobile Documents/iCloud~md~obsidian/Documents/Master_vault/Labbook')
    file_path = path / f"{filename}.md"
    preamble = """---
Experiment_group: 
Repetition:
---
Tags: #Labbook 
# Aim of experiment
Lorem ipsum
***

# Injection

"""
    epilog = """**Injection stage:**  # cell stage
**Incubation at:** ## ºC
"""
    if not file_path.exists():
        with open(file_path, 'w') as f:
            f.write(preamble)
            for injection_dict in injection_dicts:
                f.write(calc_injectionmix(injection_dict))
                f.write("\n")
            f.write(epilog)
            f.write("***\n")
    else:
        # override = input(f"File <{filename}> already exists. Do you want to overwrite it? (y/n): ")
        if override:
            print(f"Overwriting file: {file_path}")
            with open(file_path, 'w') as f:
                f.write(preamble)
                for injection_dict in injection_dicts:
                    f.write(calc_injectionmix(injection_dict))
                    f.write("\n")
                f.write(epilog)
                f.write("***\n")

        else:
            print("File not overwritten.")
