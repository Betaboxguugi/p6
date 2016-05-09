def constraint2(a):
    if 'Elise' in a:
        return False
    else:
        return True

RuleColumnPredicate(table_name='FriendList',
                    constraint_function=constraint2,
                    column_names=['firstname'],
                    column_names_exclude=False,
                    return_list=True)


def constraint1(a, b, c):
    if a + b == c:
        return True
    else:
        return False

RuleColumnPredicate(table_name='CompanyBudget',
                    constraint_function=constraint1,
                    column_names=['spending', 'earnings', 'surplus'],
                    column_names_exclude=False,
                    return_list=False)