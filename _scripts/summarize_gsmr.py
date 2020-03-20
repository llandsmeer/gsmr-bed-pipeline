import sys
import collections

GSMR_HEADER = 'Exposure Outcome bxy se p nsnp'

GSMROutRow = collections.namedtuple('GSMROutRow', 'raw ' + GSMR_HEADER)
QTL1_2SERow = collections.namedtuple('QTL1_2SERow', 'raw phenotype pheno_chr pheno_start pheno_end strand nsnps dist genotype geno_chr geno_start geno_end p_nom r2 beta se best')

def read_gsmr_out(filename):
    with open(filename) as f:
        header = next(f)
        assert GSMR_HEADER.split() == header.split()
        for line in f:
            row = GSMROutRow(line.strip(), *line.split())
            yield row

def read_qtltools(filename):
    with open(filename) as f:
        for line in f:
            row = QTL1_2SERow(line.strip(), *line.split())
            yield row

def extract_qtls(filename, keep):
    res = collections.defaultdict(dict) # { phenotype : { genotype : row }
    for row in read_qtltools(filename):
        if row.phenotype in keep:
            geno = row.genotype
            if geno.endswith(',.'): geno = geno[:-2]
            res[row.phenotype][geno] = row
    return dict(res)

def format_region(row):
    if row.pheno_start != row.pheno_end:
        return '{pheno_chr}:{pheno_start}-{pheno_end}'.format(**row._asdict())
    else:
        return '{pheno_chr}:{pheno_start}'.format(**row._asdict())

def main(gsmr_out_filename, exposure_qtls_filename, outcome_qtls_filename):
    gsmr_rows = []
    keep_exposures = set()
    keep_outcomes = set()
    for row in read_gsmr_out(gsmr_out_filename):
        gsmr_rows.append(row)
        keep_exposures.add(row.Exposure)
        keep_outcomes.add(row.Outcome)
    exposures = extract_qtls(exposure_qtls_filename, keep_exposures)
    outcomes = extract_qtls(outcome_qtls_filename, keep_outcomes)
    print(GSMR_HEADER, 'exposure_region', 'outcome_region', 'common_snps')
    for row in gsmr_rows:
        exposure = exposures.get(row.Exposure, outcomes.get(row.Exposure))
        outcome = exposures.get(row.Outcome, outcomes.get(row.Outcome))
        first_exposure = next(iter(exposure.values()))
        first_outcome = next(iter(outcome.values()))
        exposure_region = format_region(first_exposure)
        outcome_region = format_region(first_outcome)
        common_genotypes = set(exposure) & set(outcome)
        print(*row.raw.split(),  exposure_region, outcome_region, ';'.join(common_genotypes))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        gsmr_out_filename = 'jobdir/21.gsmr'
        exposure_qtls_filename = 'jobdir/21/exposure/exposure.nom.txt'
        outcome_qtls_filename = 'jobdir/21/outcome/outcome.nom.txt'
    else:
        gsmr_out_filename = sys.argv[1]
        exposure_qtls_filename = sys.argv[2]
        outcome_qtls_filename = sys.argv[3]
    main(gsmr_out_filename, exposure_qtls_filename, outcome_qtls_filename)