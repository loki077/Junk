#include <iostream>
#include <chrono>
#include <stack>

struct Node {
    int value;
    Node* left;
    Node* right;

    Node(int value) : value(value), left(nullptr), right(nullptr) {}
};

Node* createTree() {
    Node* root = new Node(1);
    root->left = new Node(2);
    root->right = new Node(3);

    root->left->left = new Node(4);
    root->left->right = new Node(5);
    root->right->right = new Node(6);

    root->left->right->left = new Node(7);
    root->right->right->left = new Node(8);
    root->right->right->right = new Node(9);

    root->left->right->left->right = new Node(10);
    return root;
}

int maxDepth(Node* root) {
    if (root == nullptr) {
        return 0;
    }

    std::stack<std::pair<Node*, int>> stack;
    int maxDepth = 0;
    stack.push(std::make_pair(root, 1));

    while (!stack.empty()) {
        auto current = stack.top().first;
        int depth = stack.top().second;
        stack.pop();

        maxDepth = std::max(maxDepth, depth);

        if (current->left) {
            stack.push(std::make_pair(current->left, depth + 1));
        }
        if (current->right) {
            stack.push(std::make_pair(current->right, depth + 1));
        }
    }

    return maxDepth;
}

int main() {
    Node* root = createTree();
    auto start = std::chrono::high_resolution_clock::now();
    int depth = maxDepth(root);
    auto end = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    std::cout << "Max depth of the tree: " << depth << std::endl;
    std::cout << "Execution Time: " << duration.count() << " ns" << std::endl;

    return 0;
}
