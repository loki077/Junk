#include <iostream>
#include <chrono>
/* 
*   @file max_depth_binary_tree.cpp
*   @brief This is a example to find the max depth of the tree
*   The tree structure is predefined as follows:
*   
*                 1
*                / \
*               2   3
*              / \   \
*             4   5   6
*                /   / \
*               7   8   9
*               \
*                10
*
*   Execution time is measured using the chrono library to assess performance.
*/

// Comment: Using namespace in this example but I am aware of namespace pollution
using namespace std;

// Comment: using safe Template to delete pointer
template <typename T>
inline void SafeDeletePointer(T& pointer)
{
    if(pointer){
    delete pointer;
    pointer = nullptr;    // Comment: just to secure if in case someone uses the pointer in future (part of good practise to follow)
    }
}

// Comment: I would prefer to use a class object and not structure but going by the Question
struct Node {
    int value;
    Node* left;
    Node* right;

    // Constructor
    Node(int val) : value(val), left(nullptr), right(nullptr) {}

    // Destructor
    ~Node() {
        SafeDeletePointer(left);
        SafeDeletePointer(right);
    }
};

// create a instance of the node
Node* newNode(const int& value) {
    return new Node(value);
}

// creating the tree
Node* createTree() {
    Node* root = newNode(1);
    root->left = newNode(2);
    root->right = newNode(3);

    root->left->left = newNode(4);
    root->left->right = newNode(5);
    root->right->right = newNode(6);

    root->left->right->left = newNode(7);
    root->right->right->left = newNode(8);
    root->right->right->right = newNode(9);

    root->left->right->left->right = newNode(10);
    return root;
}

//max depth function
int maxDepth(const Node* node) 
{
    //returning if you passed a null
    if (node == nullptr) {        
        return 0;
    } 
    else {
        // get left depth first and than right
        int leftDepth = maxDepth(node->left);
        int rightDepth = maxDepth(node->right);
        return (leftDepth > rightDepth) ? (leftDepth + 1) : (rightDepth + 1);
    }
}


int main(){
    //creating the tree
    Node* root = createTree();

    //starting the timer
    auto start = std::chrono::high_resolution_clock::now();
    int depth = maxDepth(root);
    auto end = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    std::cout << "Max depth of the tree: " << depth << std::endl;
    std::cout << "Execution Time: " << duration.count() << " ns" << std::endl;
    
    SafeDeletePointer(root); //delete the pointer created
    return 0;
}