import os
import pandas as pd
from statsmodels.stats.weightstats import ttest_ind, CompareMeans, DescrStatsW

df = pd.read_csv(os.path.join(os.path.abspath(""), "data/student_tests.csv"))

t_stat, p_value, def_freedom = ttest_ind(df["Treatment Group"], df["Control Group"], alternative='larger', usevar='unequal')
print(f"t-statistic: {t_stat}, p-value: {p_value}")

# Descriptive statistics
control_stats = DescrStatsW(df["Control Group"])
treatment_stats = DescrStatsW(df["Treatment Group"])

cm = CompareMeans(treatment_stats, control_stats)

# Calculate the confidence interval for the difference in means
confidence_interval = cm.tconfint_diff(alpha=0.05, alternative='two-sided')

print(f"95% confidence interval for the difference in means: {confidence_interval}")