
#include "pluh.h"

pluh_obj_t fun(pluh_obj_t unit, pluh_env_t *e)
{
    pluh_obj_t list1Num = call(e->data[1], (pluh_obj_t)(0));
    pluh_obj_t list2Num = call(e->data[1], (pluh_obj_t)(0));
    pluh_obj_t isNoMoreInput = call(e->data[2], list1Num);
    pluh_obj_t if_result;
    if (isNoMoreInput)
        goto if_result_true;
    pluh_obj_t recList = call(e->data[0], (pluh_obj_t)(0));
    pluh_obj_t n2 = (((pluh_tup_t *)(recList))->data[0]);
    pluh_obj_t n3 = pluh_tup_create(2, list1Num, n2);

    pluh_obj_t closure = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t list1 = call(call(closure, (pluh_obj_t)(intptr_t)(1)), n3);
    pluh_obj_t n4 = (((pluh_tup_t *)(recList))->data[1]);
    pluh_obj_t n5 = pluh_tup_create(2, list2Num, n4);

    pluh_obj_t closure1 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t list2 = call(call(closure1, (pluh_obj_t)(intptr_t)(1)), n5);
    if_result = pluh_tup_create(2, list1, list2);
    goto if_result_after;
if_result_true:

    pluh_obj_t closure2 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t n = call(call(closure2, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));

    pluh_obj_t closure3 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    pluh_obj_t n1 = call(call(closure3, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));
    if_result = pluh_tup_create(2, n, n1);
if_result_after:
    return if_result;
}

pluh_obj_t fun1(pluh_obj_t num, pluh_env_t *e)
{
    pluh_obj_t match_value;
    match_value = e->data[3];
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
    match_result = (pluh_obj_t)(intptr_t)(0);
    goto match_value_after;
match_value_Cons:
    pluh_obj_t x = ((pluh_variant_t *)(match_value))->data;
    pluh_obj_t head = (((pluh_tup_t *)(x))->data[0]);
    pluh_obj_t restOfList = (((pluh_tup_t *)(x))->data[1]);
    pluh_obj_t n6 = call(e->data[1], restOfList);
    pluh_obj_t countInRestOfList = call(n6, num);
    pluh_obj_t n7 = call(e->data[2], head);
    pluh_obj_t n8 = call(n7, num);
    pluh_obj_t if_result1;
    if (n8)
        goto if_result1_true;
    if_result1 = countInRestOfList;
    goto if_result1_after;
if_result1_true:
    pluh_obj_t n9 = call(e->data[0], (pluh_obj_t)(intptr_t)(1));
    if_result1 = call(n9, countInRestOfList);
if_result1_after:
    match_result = if_result1;
    goto match_value_after;
match_value_after:
    return match_result;
}

pluh_obj_t fun2(pluh_obj_t list3, pluh_env_t *e)
{

    pluh_obj_t closure4 = pluh_closure_create((pluh_obj_t)(fun1), 4, e->data[0], e->data[1], e->data[2], list3);
    return closure4;
}

pluh_obj_t fun3(pluh_obj_t callback, pluh_env_t *e)
{
    pluh_obj_t match_value1;
    match_value1 = e->data[0];
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

    pluh_obj_t closure5 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    match_result1 = call(call(closure5, (pluh_obj_t)(intptr_t)(0)), (pluh_obj_t)(0));
    goto match_value1_after;
match_value1_Cons:
    pluh_obj_t x1 = ((pluh_variant_t *)(match_value1))->data;
    pluh_obj_t head1 = (((pluh_tup_t *)(x1))->data[0]);
    pluh_obj_t restOfList1 = (((pluh_tup_t *)(x1))->data[1]);
    pluh_obj_t n10 = call(callback, head1);
    pluh_obj_t n11 = call(e->data[1], restOfList1);
    pluh_obj_t n12 = call(n11, callback);
    pluh_obj_t n13 = pluh_tup_create(2, n10, n12);

    pluh_obj_t closure6 = pluh_closure_create((pluh_obj_t)(pluh_rt_make_variant), 0);
    match_result1 = call(call(closure6, (pluh_obj_t)(intptr_t)(1)), n13);
    goto match_value1_after;
match_value1_after:
    return match_result1;
}

pluh_obj_t fun4(pluh_obj_t list4, pluh_env_t *e)
{

    pluh_obj_t closure7 = pluh_closure_create((pluh_obj_t)(fun3), 2, list4, e->data[0]);
    return closure7;
}

pluh_obj_t fun5(pluh_obj_t init, pluh_env_t *e)
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
    match_result2 = init;
    goto match_value2_after;
match_value2_Cons:
    pluh_obj_t x2 = ((pluh_variant_t *)(match_value2))->data;
    pluh_obj_t head2 = (((pluh_tup_t *)(x2))->data[0]);
    pluh_obj_t restOfList2 = (((pluh_tup_t *)(x2))->data[1]);
    pluh_obj_t n14 = call(e->data[0], head2);
    pluh_obj_t n15 = call(e->data[2], restOfList2);
    pluh_obj_t n16 = call(n15, e->data[0]);
    pluh_obj_t n17 = call(n16, init);
    match_result2 = call(n14, n17);
    goto match_value2_after;
match_value2_after:
    return match_result2;
}

pluh_obj_t fun6(pluh_obj_t callback1, pluh_env_t *e)
{

    pluh_obj_t closure8 = pluh_closure_create((pluh_obj_t)(fun5), 3, callback1, e->data[0], e->data[1]);
    return closure8;
}

pluh_obj_t fun7(pluh_obj_t list5, pluh_env_t *e)
{

    pluh_obj_t closure9 = pluh_closure_create((pluh_obj_t)(fun6), 2, list5, e->data[0]);
    return closure9;
}

pluh_obj_t fun8(pluh_obj_t elem, pluh_env_t *e)
{
    pluh_obj_t n19 = call(e->data[2], elem);
    pluh_obj_t n20 = call(e->data[0], e->data[1]);
    pluh_obj_t n21 = call(n20, elem);
    return call(n19, n21);
}

int main(void)
{
    pluh_init();
    (void)((pluh_obj_t)(0));
    pluh_obj_t getTwoListsFromUser = pluh_closure_create((pluh_obj_t)(fun), 3, getTwoListsFromUser, geti, iszero);
    ((pluh_closure_t *)(getTwoListsFromUser))->e.data[0] = getTwoListsFromUser;
    pluh_obj_t countOccurrencesInList = pluh_closure_create((pluh_obj_t)(fun2), 3, addi, countOccurrencesInList, eqi);
    ((pluh_closure_t *)(countOccurrencesInList))->e.data[1] = countOccurrencesInList;
    pluh_obj_t map = pluh_closure_create((pluh_obj_t)(fun4), 1, map);
    ((pluh_closure_t *)(map))->e.data[0] = map;
    pluh_obj_t reduce = pluh_closure_create((pluh_obj_t)(fun7), 1, reduce);
    ((pluh_closure_t *)(reduce))->e.data[0] = reduce;
    pluh_obj_t twoLists = call(getTwoListsFromUser, (pluh_obj_t)(0));
    pluh_obj_t list11 = (((pluh_tup_t *)(twoLists))->data[0]);
    pluh_obj_t list21 = (((pluh_tup_t *)(twoLists))->data[1]);
    pluh_obj_t n18 = call(map, list11);

    pluh_obj_t closure10 = pluh_closure_create((pluh_obj_t)(fun8), 3, countOccurrencesInList, list21, muli);
    pluh_obj_t n22 = closure10;
    pluh_obj_t scores = call(n18, n22);
    pluh_obj_t n23 = call(reduce, scores);
    pluh_obj_t n24 = call(n23, addi);
    pluh_obj_t score = call(n24, (pluh_obj_t)(intptr_t)(0));
    return (int)(intptr_t)(call(puti, score));
}
