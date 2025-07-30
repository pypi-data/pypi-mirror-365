#include <stdio.h>

struct Point {
    int x;
    int y;
};

int main() {
    struct Point p = {3, 4};
    printf("%d %d\n", p.x, p.y);
    return 0;
}
