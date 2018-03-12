/*
 * Basic definitions/types
 * Copyright (C) 2009-2014 Wray Buntine
 * All rights reserved.
 *
 * This Source Code Form is subject to the terms of the Mozilla
 * Public License, v. 2.0. If a copy of the MPL was not
 * distributed with this file, You can obtain one at
 *      http://mozilla.org/MPL/2.0/.
 *
 * Author: Wray Buntine (wray.buntine@monash.edu)
 *
 *
 */
#ifndef __HCA_H
#define __HCA_H

/*
 *  this is defined in "stats.h"
 *  #define NG_SCALESTATS
 */

#include <unistd.h>
#include "lgamma.h"
#include "util.h"
#include "stable.h"
#include "pctl.h"
#include "stats.h"
#include "srng.h"

#define HCA_VERSION "0.63"

/*
 *   Switch on to allow threading
 *   if off some vestiges remain but wont call threads
 *  NB.  not usually done here, done in the Makefile
 */
// #define H_THREADS

/*
 *   when defined, stops introducing new topics into a
 *   document after the first ... ???
 */
// #define GIBBS_ZEROD

/*
 *   Allow experimental stuff ... only for developers since
 *   they mostly don't work
 */
// #define EXPERIMENTAL
/*
 *   when defined does tracking of changes to a single Nwt
 *   during sampling
 */
// #define TRACE_WT
#ifdef TRACE_WT
#define TR_W 4744
#define TR_T 7
#endif

#ifndef HCA_MIN_DOCS
/*
 *   minimum allowed # of docs (was formerly 5)
 */
// #define HCA_MIN_DOCS
#define HCA_MIN_DOCS 1
#define HCA_STR(x) #x
#define HCA_MIN_DOCS_STR() HCA_STR(HCA_MIN_DOCS)
#endif

/*
 *    used when printing words
 */
enum ScoreType { ST_count, ST_idf, ST_cost, ST_Q, ST_phi, ST_phirat };

double likelihood();

double lp_test_Pred(char *resstem);
#ifdef EXPERIMENTAL
double lp_test_LRS();
#endif
double lp_test_ML(int procs, enum GibbsType fix);

float **hca_topmtx();
void like_merge(float minprop, double scale, int best);

void query_read(char *fname);
void gibbs_query(char *stem, int K, char *qname, int dots, int procs,
		 int doexclude, float scale);

void print_maxz(char *fname);

void predict_topk(char *resstem, int topk);


//==================================================
// global variables
//==================================================

extern rngp_t rngp;
extern int verbose;

#endif
