
def validate_data(calc_df):

    errors = []

    for idx, row in calc_df.iterrows():

        student = idx + 1

        # -------------------------
        # MT Checks
        # -------------------------

        if row["MT1"] > 70:
            errors.append(f"Student {student}: MT1 > 70")

        if row["MT2"] > 70:
            errors.append(f"Student {student}: MT2 > 70")

        # -------------------------
        # CO Maximum Checks
        # -------------------------

        if row["CO1(28)"] > 28:
            errors.append(f"Student {student}: CO1 > 28")
        if row["CO2(28)"] > 28:
                errors.append(f"Student {student}: CO2 > 28")

        if row["CO3_M1(14)"] > 14:
                errors.append(f"Student {student}: CO3(MT1) > 14")

        if row["CO3_M2(14)"] > 14:
                errors.append(f"Student {student}: CO3(MT2) > 14")

        if row["CO4(28)"] > 28:
                errors.append(f"Student {student}: CO4 > 28")

        if row["CO5(28)"] > 28:
                errors.append(f"Student {student}: CO5 > 28")

            # -------------------------
            # Sum Checks
            # -------------------------

        if row["CO1(28)"] + row["CO2(28)"] + row["CO3_M1(14)"] != row["MT1"]:
                errors.append(f"Student {student}: MT1 sum mismatch")

        if row["CO3_M2(14)"] + row["CO4(28)"] + row["CO5(28)"] != row["MT2"]:
              errors.append(f"Student {student}: MT2 sum mismatch")

        # -------------------------
        # Difference Checks
        # -------------------------

        if abs(row["CO1(28)"] - row["CO2(28)"]) > 3:
            errors.append(f"Student {student}: CO1 & CO2 differ by more than 3")

        if abs(row["CO4(28)"] - row["CO5(28)"]) > 3:
            errors.append(f"Student {student}: CO4 & CO5 differ by more than 3")

    return errors