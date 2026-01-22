#include <stdio.h>
#include <string.h>
int main() {
	int cnt[26] = {0};
	int t; scanf("%d", &t);
	for (;t--;) {
		char one[3], two[3];
		scanf("%s%s", one, two);
		memset(cnt, 0, 26 * sizeof(int));
		for (int i = 0; i < 2; ++i) {
			cnt[one[i] - 'a']++;
			cnt[two[i] - 'a']++;
		}
		int c = 0;
		for (int i = 0; i < 26; ++i) if (cnt[i]) c++;
		printf("%d\n", c - 1);
	}
}
