#include <stdio.h>
#include <stdlib.h>
int main() {
int t; scanf("%d", &t);
for (;t--;) {

	int n; scanf("%d", &n);
	int* there = calloc(2 * n, sizeof(int));
	int* ans = calloc(2 * n, sizeof(int));

	for (int x = 0; x < n; ++x) {
		for (int y = 0; y < n; ++y) {
			int temp; scanf("%d", &temp);
			ans[1 + x + y] = temp;
			there[temp - 1] = 1;
		}
	}
	
	int absent_len = 0;
	for (int x = 0; x < 2 * n; ++x) absent_len += there[x];
	int* absent = malloc(sizeof(int) * absent_len);
	int i = 0;
	for (int x = 1; x < 2 * n + 1; ++x) {
		if (!there[x - 1]) {
			absent[i] = x;
			++i;
		}
	}
	i = 0;
	for (int x = 0; x < 2 * n; ++x) {
		if (ans[x]) printf("%d ", ans[x]);
		else {
			printf("%d ", absent[i]);
			++i;
		}
	}
	printf("\n");



}
}
