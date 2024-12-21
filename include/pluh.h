#ifndef PLUH_H
#define PLUH_H

#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define CHECK(p)                                                                                                       \
    do                                                                                                                 \
    {                                                                                                                  \
        if (!p)                                                                                                        \
        {                                                                                                              \
            perror(#p);                                                                                                \
            abort();                                                                                                   \
        }                                                                                                              \
    } while (0)

#define ALLOC(p, n)                                                                                                    \
    do                                                                                                                 \
    {                                                                                                                  \
        p = calloc(n, sizeof(*p));                                                                                     \
        CHECK(p);                                                                                                      \
    } while (0)

typedef void                 *pluh_obj_t;
typedef struct pluh_tup_s     pluh_tup_t;
typedef struct pluh_tup_s     pluh_env_t;
typedef struct pluh_variant_s pluh_variant_t;
typedef struct pluh_closure_s pluh_closure_t;
typedef pluh_obj_t (*pluh_closure_cb_t)(pluh_obj_t, pluh_env_t *);

struct pluh_tup_s
{
    pluh_obj_t *data;
};

struct pluh_closure_s
{
    pluh_closure_cb_t f;
    pluh_env_t        e;
};

struct pluh_variant_s
{
    int        type;
    pluh_obj_t data;
};

pluh_closure_t *pluh_closure_create(pluh_obj_t f, int n, ...);
pluh_tup_t     *pluh_tup_create(int n, ...);
pluh_variant_t *pluh_variant_create(int n, pluh_obj_t o);
pluh_obj_t      call(pluh_obj_t l, pluh_obj_t r);
pluh_obj_t      pluh_rt_make_variant(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_addi(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_subi(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_muli(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_divi(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_puti(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_geti(pluh_obj_t o, pluh_env_t *e);
pluh_obj_t      pluh_rt_iszero(pluh_obj_t o, pluh_env_t *e);
void            pluh_init(void);

extern pluh_obj_t addi;
extern pluh_obj_t subi;
extern pluh_obj_t muli;
extern pluh_obj_t divi;
extern pluh_obj_t puti;
extern pluh_obj_t geti;
extern pluh_obj_t iszero;

#endif // PLUH_H
