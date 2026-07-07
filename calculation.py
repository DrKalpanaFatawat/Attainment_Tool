
import pandas as pd
def calculate_mt(calc_df, sessional_col):

    # -----------------------------
    # Convert Sessional (30) → 70
    # -----------------------------

    calc_df[sessional_col] = pd.to_numeric(
        calc_df[sessional_col],
        errors="coerce"
    )

    calc_df = calc_df.dropna(subset=[sessional_col])

    calc_df["Converted70"] = (
        calc_df[sessional_col] * 70 / 30
    ).round().astype(int)

    # -----------------------------
    # Double Total
    # -----------------------------

    calc_df["DoubleTotal"] = calc_df["Converted70"] * 2

    # -----------------------------
    # MT1 / MT2
    # -----------------------------

    mt1_list = []
    mt2_list = []

    offsets = [0, -1, 1, -2, 2, 0]

    for i, total in enumerate(calc_df["DoubleTotal"]):

        base = total // 2

        if total == 140:

            mt1 = 70
            mt2 = 70

        else:

            mt1 = base + offsets[i % len(offsets)]
            mt2 = total - mt1

            if mt1 > 70:
                excess = mt1 - 70
                mt1 = 70
                mt2 += excess

            if mt2 > 70:
                excess = mt2 - 70
                mt2 = 70
                mt1 += excess

            mt1 = min(mt1, 70)
            mt2 = min(mt2, 70)

        mt1_list.append(mt1)
        mt2_list.append(mt2)

    calc_df["MT1"] = mt1_list
    calc_df["MT2"] = mt2_list

    return calc_df