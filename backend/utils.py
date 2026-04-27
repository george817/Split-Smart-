def calculate_splits(df, members):
    if df.empty:
        return [], 0
    total = df['amount'].sum()
    per_person = total / len(members)
    paid = df.groupby('paid_by')['amount'].sum().reindex(members, fill_value=0)
    balances = paid - per_person

    owes = []
    creditors = balances[balances > 0].sort_values(ascending=False)
    debtors = balances[balances < 0].sort_values()
    c_list = list(creditors.items())
    d_list = list(debtors.items())
    i, j = 0, 0

    while i < len(c_list) and j < len(d_list):
        creditor, credit = c_list[i]
        debtor, debt = d_list[j]
        debt = abs(debt)
        settled = min(credit, debt)
        owes.append({"from": debtor, "to": creditor, "amount": round(settled, 2)})
        c_list[i] = (creditor, credit - settled)
        d_list[j] = (debtor, -(debt - settled))
        if c_list[i][1] < 0.01:
            i += 1
        if abs(d_list[j][1]) < 0.01:
            j += 1

    return owes, round(per_person, 2)
