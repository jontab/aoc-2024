#include "pluh.h"

#include <assert.h>

pluh_obj_t addi = NULL;
pluh_obj_t subi = NULL;
pluh_obj_t muli = NULL;
pluh_obj_t divi = NULL;
pluh_obj_t puti = NULL;
pluh_obj_t geti = NULL;
pluh_obj_t iszero = NULL;

static pluh_obj_t pluh_make_variant_2(pluh_obj_t o, pluh_env_t *e);
static pluh_obj_t pluh_rt_addi_2(pluh_obj_t o, pluh_env_t *e);
static pluh_obj_t pluh_rt_subi_2(pluh_obj_t o, pluh_env_t *e);
static pluh_obj_t pluh_rt_muli_2(pluh_obj_t o, pluh_env_t *e);
static pluh_obj_t pluh_rt_divi_2(pluh_obj_t o, pluh_env_t *e);

pluh_closure_t *pluh_closure_create(pluh_obj_t f, int n, ...)
{
    pluh_closure_t *c;
    ALLOC(c, 1);

    c->f = f;
    ALLOC(c->e.data, n);

    va_list args;
    va_start(args, n);

    for (int i = 0; i < n; i++)
        c->e.data[i] = va_arg(args, pluh_obj_t);

    va_end(args);
    return c;
}

pluh_tup_t *pluh_tup_create(int n, ...)
{
    pluh_tup_t *t;
    ALLOC(t, 1);
    ALLOC(t->data, n);

    va_list args;
    va_start(args, n);

    for (int i = 0; i < n; i++)
        t->data[i] = va_arg(args, pluh_obj_t);

    va_end(args);
    return t;
}

pluh_variant_t *pluh_variant_create(int n, pluh_obj_t o)
{
    pluh_variant_t *s;
    ALLOC(s, 1);
    s->type = n;
    s->data = o;
    return s;
}

pluh_obj_t call(pluh_obj_t l, pluh_obj_t r)
{
    pluh_closure_t *c = (pluh_closure_t *)(l);
    return c->f(r, &c->e);
}

void pluh_init(void)
{
    addi = pluh_closure_create((pluh_obj_t)(pluh_rt_addi), 0);
    subi = pluh_closure_create((pluh_obj_t)(pluh_rt_subi), 0);
    muli = pluh_closure_create((pluh_obj_t)(pluh_rt_muli), 0);
    divi = pluh_closure_create((pluh_obj_t)(pluh_rt_divi), 0);
    puti = pluh_closure_create((pluh_obj_t)(pluh_rt_puti), 0);
    geti = pluh_closure_create((pluh_obj_t)(pluh_rt_geti), 0);
    iszero = pluh_closure_create((pluh_obj_t)(pluh_rt_iszero), 0);
}

pluh_obj_t pluh_rt_make_variant(pluh_obj_t o, pluh_env_t *e)
{
    return pluh_closure_create((pluh_obj_t)(pluh_make_variant_2), 1, o);
}

pluh_obj_t pluh_rt_addi(pluh_obj_t o, pluh_env_t *e)
{
    return pluh_closure_create((pluh_obj_t)(pluh_rt_addi_2), 1, o);
}

pluh_obj_t pluh_rt_subi(pluh_obj_t o, pluh_env_t *e)
{
    return pluh_closure_create((pluh_obj_t)(pluh_rt_subi_2), 1, o);
}

pluh_obj_t pluh_rt_muli(pluh_obj_t o, pluh_env_t *e)
{
    return pluh_closure_create((pluh_obj_t)(pluh_rt_muli_2), 1, o);
}

pluh_obj_t pluh_rt_divi(pluh_obj_t o, pluh_env_t *e)
{
    return pluh_closure_create((pluh_obj_t)(pluh_rt_divi_2), 1, o);
}

pluh_obj_t pluh_rt_puti(pluh_obj_t o, pluh_env_t *e)
{
    int i = (int)(intptr_t)(o);
    printf("%d\n", i);
    return (pluh_obj_t)(0);
}

pluh_obj_t pluh_rt_geti(pluh_obj_t o, pluh_env_t *e)
{
    int i;
    scanf("%d", &i);
    return (pluh_obj_t)(intptr_t)(i);
}

pluh_obj_t pluh_rt_iszero(pluh_obj_t o, pluh_env_t *e)
{
    int i = (int)(intptr_t)(o);
    return (pluh_obj_t)(intptr_t)(i == 0);
}

pluh_obj_t pluh_make_variant_2(pluh_obj_t o, pluh_env_t *e)
{
    int type = (int)(intptr_t)(e->data[0]);
    return pluh_variant_create(type, o);
}

pluh_obj_t pluh_rt_addi_2(pluh_obj_t o, pluh_env_t *e)
{
    int x = (int)(intptr_t)(e->data[0]);
    int y = (int)(intptr_t)(o);
    return (pluh_obj_t)(intptr_t)(x + y);
}

pluh_obj_t pluh_rt_subi_2(pluh_obj_t o, pluh_env_t *e)
{
    int x = (int)(intptr_t)(e->data[0]);
    int y = (int)(intptr_t)(o);
    return (pluh_obj_t)(intptr_t)(x - y);
}

pluh_obj_t pluh_rt_muli_2(pluh_obj_t o, pluh_env_t *e)
{
    int x = (int)(intptr_t)(e->data[0]);
    int y = (int)(intptr_t)(o);
    return (pluh_obj_t)(intptr_t)(x * y);
}

pluh_obj_t pluh_rt_divi_2(pluh_obj_t o, pluh_env_t *e)
{
    int x = (int)(intptr_t)(e->data[0]);
    int y = (int)(intptr_t)(o);
    return (pluh_obj_t)(intptr_t)(x / y);
}
