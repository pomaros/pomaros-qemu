/* SPDX-License-Identifier: MIT */
/* Copyright (c) 2026 John Knipper */
#include <pthread.h>
#include <sched.h>
#include <errno.h>
#include <stdio.h>
#include <stdint.h>
#include <proto/exec.h>
#include <exec/semaphores.h>
static pthread_mutex_t shared=PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t recursive=PTHREAD_RECURSIVE_MUTEX_INITIALIZER;
static pthread_mutex_t checked=PTHREAD_ERRORCHECK_MUTEX_INITIALIZER;
static unsigned start,failed;
static unsigned count;
static void *worker(void *unused) {
    (void)unused;
    while (!__atomic_load_n(&start,__ATOMIC_ACQUIRE)) sched_yield();
    for (unsigned i=0;i<500;i++) {
        int e=pthread_mutex_lock(&shared);
        if(e) {__atomic_store_n(&failed,1,__ATOMIC_RELEASE);return 0;}
        count++;
        if(pthread_mutex_unlock(&shared)) {__atomic_store_n(&failed,1,__ATOMIC_RELEASE);return 0;}
    }
    return 0;
}
#define CHECK(c) do {if(!(c)){printf("[FIRSTUSE] FAIL line=%d\n",__LINE__);return 20;}} while(0)
int main(void) {
    pthread_t threads[8];
    struct SignalSemaphore sem={0};ULONG state=0;
    CHECK(InitSemaphoreOnce(&sem,&state,SSINITF_TRY));
    CHECK(state==1&&InitSemaphoreOnce(&sem,&state,0));
    state=2;CHECK(!InitSemaphoreOnce(&sem,&state,0));
    for(unsigned i=0;i<8;i++) CHECK(!pthread_create(&threads[i],0,worker,0));
    __atomic_store_n(&start,1,__ATOMIC_RELEASE);
    for(unsigned i=0;i<8;i++) CHECK(!pthread_join(threads[i],0));
    CHECK(!failed&&count==4000&&shared.initialized==1);
    CHECK(!pthread_mutex_lock(&recursive));CHECK(!pthread_mutex_trylock(&recursive));
    CHECK(!pthread_mutex_unlock(&recursive));CHECK(!pthread_mutex_unlock(&recursive));
    CHECK(!pthread_mutex_lock(&checked));CHECK(pthread_mutex_trylock(&checked)==EBUSY);
    CHECK(pthread_mutex_lock(&checked)==EDEADLK);CHECK(!pthread_mutex_unlock(&checked));
    CHECK(!pthread_mutex_destroy(&shared));CHECK(!pthread_mutex_destroy(&recursive));
    CHECK(!pthread_mutex_destroy(&checked));
    puts("[FIRSTUSE] result=PASS threads=8 increments=4000 recursive=PASS errorcheck=PASS exec-once=PASS");
    return 0;
}
