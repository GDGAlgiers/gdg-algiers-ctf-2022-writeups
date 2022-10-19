#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#define MAX 100
#include <string.h>
int main()
{
    char a[MAX];
    fprintf(stdout, "Let me check your secret: ");
    fgets(a, MAX, stdin);
    srand(time(NULL)); 
    int r1 = rand(); 
    int r2 = rand(); 
    int r3 = rand(); 
    if (r1 == r2 && r2 == r3 && a[0] * r1 == r3) {
        int fl4g[] = {6, 60, 39, 32, 55, 0, 55, 48, 33, 44, 49, 32, 54, 62, 97, 32, 0, 26, 43, 10, 49, 45, 12, 11, 2, 26, 12, 97, 26, 116, 40, 53, 42, 97, 97, 44, 7, 41, 32, 56};
        char fl44444g[] = "";
        int hehe = 69; 
        for (int x = 0; x < 40; x++) {
            char ch = fl4g[x] ^ hehe;
            strncat(fl44444g, &ch, 1);
        } 
        // printf("%s\n", fl44444g);
    }
    else fprintf(stdout, "\nHmmm, that seems wrong");
    fprintf(stdout, "\n");
    return 0;
}
