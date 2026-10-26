/* SPDX-License-Identifier: MIT */
/* Copyright (c) 2026 John Knipper */
#include <stdio.h>
#include <errno.h>
#include <string.h>
#define CHECK(c) do {if(!(c)){printf("[RENAME] FAIL line=%d errno=%d\n",__LINE__,errno);return 20;}} while(0)
static int put(const char *path,const char *text) {FILE*f=fopen(path,"wb");if(!f)return 0;size_t n=strlen(text);int ok=fwrite(text,1,n,f)==n;return fclose(f)==0&&ok;}
static int is(const char *path,const char *text) {char data[80]={0};FILE*f=fopen(path,"rb");if(!f)return 0;size_t n=fread(data,1,sizeof(data)-1,f);int ok=!ferror(f)&&n==strlen(text)&&!memcmp(data,text,n);return fclose(f)==0&&ok;}
int main(void) {
    const char *src="RAM:runtime-candidate-rename-source",*dst="RAM:runtime-candidate-rename-target",*missing="RAM:runtime-candidate-rename-absent";
    remove(src);remove(dst);remove(missing);
    CHECK(put(src,"source payload"));CHECK(put(dst,"old target"));
    CHECK(rename(src,dst)==0);CHECK(is(dst,"source payload"));
    FILE*f=fopen(src,"rb");CHECK(f==0);
    errno=0;CHECK(rename(missing,dst)==-1);CHECK(errno==ENOENT);CHECK(is(dst,"source payload"));
    CHECK(rename(dst,dst)==0);CHECK(is(dst,"source payload"));
    CHECK(remove(dst)==0);
    puts("[RENAME] result=PASS replacement=PASS missing-source-preserves-target=PASS same-path=PASS");return 0;
}
