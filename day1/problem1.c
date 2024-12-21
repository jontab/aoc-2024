
#include "pluh.h"

pluh_obj_t fun(pluh_obj_t num, pluh_env_t *e)
{
    pluh_obj_t match_value;
    match_value = e->data[1];
    switch (((pluh_variant_t *)(match_value))->type)
    {
    case 0:
        goto match_value_Leaf;
    case 1:
        goto match_value_Cons;
    default:
        abort();
    }

    pluh_obj_t match_result;
match_value_Leaf:

    pluh_obj_t closure = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t n = call(call(closure, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));
    pluh_obj_t n1 = pluh_tup_create(2, num, n);

    pluh_obj_t closure1 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    match_result = call(call(closure1, (pluh_obj_t)(intptr_t)(1)), n1);
    goto match_value_after;
match_value_Cons:
    pluh_obj_t x = ((pluh_variant_t *)(match_value))->data;
    pluh_obj_t head = (((pluh_tup_t *)(x))->data[0]);
    pluh_obj_t restOfList = (((pluh_tup_t *)(x))->data[1]);
    pluh_obj_t n2 = call(e->data[2], num);
    pluh_obj_t n3 = call(n2, head);
    pluh_obj_t if_result;
    if (n3)
        goto if_result_true;
    pluh_obj_t n7 = call(e->data[0], restOfList);
    pluh_obj_t n8 = call(n7, num);
    pluh_obj_t n9 = pluh_tup_create(2, head, n8);

    pluh_obj_t closure2 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    if_result = call(call(closure2, (pluh_obj_t)(intptr_t)(1)), n9);
    goto if_result_after;
if_result_true:
    pluh_obj_t n4 = pluh_tup_create(2, head, restOfList);

    pluh_obj_t closure3 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t n5 = call(call(closure3, (pluh_obj_t)(intptr_t)(1)), n4);
    pluh_obj_t n6 = pluh_tup_create(2, num, n5);

    pluh_obj_t closure4 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    if_result = call(call(closure4, (pluh_obj_t)(intptr_t)(1)), n6);
if_result_after:
    match_result = if_result;
    goto match_value_after;
match_value_after:
    return match_result;
}

pluh_obj_t fun1(pluh_obj_t list1, pluh_env_t *e)
{

    pluh_obj_t closure5 = pluh_closure_create((pluh_obj_t)(fun), 3, e->data[0], list1, e->data[1]);
    return closure5;
}

pluh_obj_t fun2(pluh_obj_t unit, pluh_env_t *e)
{
    pluh_obj_t list1Num = call(e->data[1], (pluh_obj_t)(0));
    pluh_obj_t list2Num = call(e->data[1], (pluh_obj_t)(0));
    pluh_obj_t n10 = call(e->data[3], list1Num);
    pluh_obj_t if_result1;
    if (n10)
        goto if_result1_true;
    pluh_obj_t recursiveList = call(e->data[0], (pluh_obj_t)(0));
    pluh_obj_t n13 = (((pluh_tup_t *)(recursiveList))->data[0]);
    pluh_obj_t n14 = call(e->data[2], n13);
    pluh_obj_t list11 = call(n14, list1Num);
    pluh_obj_t n15 = (((pluh_tup_t *)(recursiveList))->data[1]);
    pluh_obj_t n16 = call(e->data[2], n15);
    pluh_obj_t list2 = call(n16, list2Num);
    if_result1 = pluh_tup_create(2, list11, list2);
    goto if_result1_after;
if_result1_true:

    pluh_obj_t closure6 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t n11 = call(call(closure6, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));

    pluh_obj_t closure7 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t n12 = call(call(closure7, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));
    if_result1 = pluh_tup_create(2, n11, n12);
if_result1_after:
    return if_result1;
}

pluh_obj_t fun3(pluh_obj_t list3, pluh_env_t *e)
{
    pluh_obj_t match_value1;
    match_value1 = list3;
    switch (((pluh_variant_t *)(match_value1))->type)
    {
    case 0:
        goto match_value1_Leaf;
    case 1:
        goto match_value1_Cons;
    default:
        abort();
    }

    pluh_obj_t match_result1;
match_value1_Leaf:
    match_result1 = (pluh_obj_t)(0);
    goto match_value1_after;
match_value1_Cons:
    pluh_obj_t x1 = ((pluh_variant_t *)(match_value1))->data;
    pluh_obj_t n17 = (((pluh_tup_t *)(x1))->data[0]);
    pluh_obj_t n18 = call(e->data[1], n17);
    pluh_obj_t n19 = (((pluh_tup_t *)(x1))->data[1]);
    pluh_obj_t n20 = call(e->data[0], n19);
    (void)(n18);
    match_result1 = n20;
    goto match_value1_after;
match_value1_after:
    return match_result1;
}

pluh_obj_t fun4(pluh_obj_t value, pluh_env_t *e)
{
    pluh_obj_t n21 = call(e->data[0], value);
    pluh_obj_t n22 = call(n21, (pluh_obj_t)(intptr_t)(0));
    pluh_obj_t if_result2;
    if (n22)
        goto if_result2_true;
    if_result2 = value;
    goto if_result2_after;
if_result2_true:
    pluh_obj_t n23 = call(e->data[1], value);
    if_result2 = call(n23, (pluh_obj_t)(intptr_t)(-1));
if_result2_after:
    return if_result2;
}

pluh_obj_t fun5(pluh_obj_t list21, pluh_env_t *e)
{
    pluh_obj_t match_value2;
    match_value2 = e->data[1];
    switch (((pluh_variant_t *)(match_value2))->type)
    {
    case 0:
        goto match_value2_Leaf;
    case 1:
        goto match_value2_Cons;
    default:
        abort();
    }

    pluh_obj_t match_result2;
match_value2_Leaf:

    pluh_obj_t closure8 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    match_result2 = call(call(closure8, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));
    goto match_value2_after;
match_value2_Cons:
    pluh_obj_t innerList1 = ((pluh_variant_t *)(match_value2))->data;
    pluh_obj_t match_value3;
    match_value3 = list21;
    switch (((pluh_variant_t *)(match_value3))->type)
    {
    case 0:
        goto match_value3_Leaf;
    case 1:
        goto match_value3_Cons;
    default:
        abort();
    }

    pluh_obj_t match_result3;
match_value3_Leaf:

    pluh_obj_t closure9 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    match_result3 = call(call(closure9, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));
    goto match_value3_after;
match_value3_Cons:
    pluh_obj_t innerList2 = ((pluh_variant_t *)(match_value3))->data;
    pluh_obj_t n24 = (((pluh_tup_t *)(innerList1))->data[0]);
    pluh_obj_t n25 = call(e->data[3], n24);
    pluh_obj_t n26 = (((pluh_tup_t *)(innerList2))->data[0]);
    pluh_obj_t headDiff = call(n25, n26);
    pluh_obj_t absDiff = call(e->data[0], headDiff);
    pluh_obj_t n27 = (((pluh_tup_t *)(innerList1))->data[1]);
    pluh_obj_t n28 = call(e->data[2], n27);
    pluh_obj_t n29 = (((pluh_tup_t *)(innerList2))->data[1]);
    pluh_obj_t restOfList1 = call(n28, n29);
    pluh_obj_t n30 = pluh_tup_create(2, absDiff, restOfList1);

    pluh_obj_t closure10 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    match_result3 = call(call(closure10, (pluh_obj_t)(intptr_t)(1)), n30);
    goto match_value3_after;
match_value3_after:
    match_result2 = match_result3;
    goto match_value2_after;
match_value2_after:
    return match_result2;
}

pluh_obj_t fun6(pluh_obj_t list12, pluh_env_t *e)
{

    pluh_obj_t closure11 = pluh_closure_create((pluh_obj_t)(fun5), 4, e->data[0], list12, e->data[1], e->data[2]);
    return closure11;
}

pluh_obj_t fun7(pluh_obj_t list4, pluh_env_t *e)
{
    pluh_obj_t match_value4;
    match_value4 = list4;
    switch (((pluh_variant_t *)(match_value4))->type)
    {
    case 0:
        goto match_value4_Leaf;
    case 1:
        goto match_value4_Cons;
    default:
        abort();
    }

    pluh_obj_t match_result4;
match_value4_Leaf:
    match_result4 = (pluh_obj_t)(intptr_t)(0);
    goto match_value4_after;
match_value4_Cons:
    pluh_obj_t innerList = ((pluh_variant_t *)(match_value4))->data;
    pluh_obj_t n31 = (((pluh_tup_t *)(innerList))->data[0]);
    pluh_obj_t n32 = call(e->data[0], n31);
    pluh_obj_t n33 = (((pluh_tup_t *)(innerList))->data[1]);
    pluh_obj_t n34 = call(e->data[1], n33);
    match_result4 = call(n32, n34);
    goto match_value4_after;
match_value4_after:
    return match_result4;
}

int main(void)
{
    pluh_init();
    (void)((pluh_obj_t)(0));
    pluh_obj_t insertIntoIncreasingList = pluh_closure_create((pluh_obj_t)(fun1), 2, insertIntoIncreasingList, lti);
    ((pluh_closure_t *)(insertIntoIncreasingList))->e.data[0] = insertIntoIncreasingList;
    pluh_obj_t buildTwoListsFromUser = pluh_closure_create((pluh_obj_t)(fun2), 4, buildTwoListsFromUser, geti, insertIntoIncreasingList, iszero);
    ((pluh_closure_t *)(buildTwoListsFromUser))->e.data[0] = buildTwoListsFromUser;
    pluh_obj_t printList = pluh_closure_create((pluh_obj_t)(fun3), 2, printList, puti);
    ((pluh_closure_t *)(printList))->e.data[0] = printList;

    pluh_obj_t closure12 = pluh_closure_create((pluh_obj_t)(fun4), 2, lti, muli);
    pluh_obj_t getAbsoluteValue = closure12;
    pluh_obj_t makeDifferenceList = pluh_closure_create((pluh_obj_t)(fun6), 3, getAbsoluteValue, makeDifferenceList, subi);
    ((pluh_closure_t *)(makeDifferenceList))->e.data[1] = makeDifferenceList;
    pluh_obj_t listSum = pluh_closure_create((pluh_obj_t)(fun7), 2, addi, listSum);
    ((pluh_closure_t *)(listSum))->e.data[1] = listSum;
    pluh_obj_t twoLists = call(buildTwoListsFromUser, (pluh_obj_t)(0));
    pluh_obj_t list13 = (((pluh_tup_t *)(twoLists))->data[0]);
    pluh_obj_t list22 = (((pluh_tup_t *)(twoLists))->data[1]);
    pluh_obj_t n35 = call(makeDifferenceList, list13);
    pluh_obj_t diffList = call(n35, list22);
    pluh_obj_t totalDiffSum = call(listSum, diffList);
    return (int)(intptr_t)(call(puti, totalDiffSum));
}
