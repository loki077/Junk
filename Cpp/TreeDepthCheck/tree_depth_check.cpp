/* search the Max depth of the tree
use the below Tree structure to do it
I don't remmeber the exact tree
                 1
                / \
               2   3
              / \   \
             4   5   6
                /   / \
               7   8   9
               \
                10

Additional I have added the time check using chrono of the execution. Obviously it has added overheads.

I have over commented to explain stuff.
*/


#include <iostream>
#include <chrono>

using namespace std;

/* Node structure as you mentioned
    left pointer to point to left child
    right pointer to point to right child
    I added value to store the location of the node
*/
// New comment: Yes you are correct I didn't create a destructure an deconstructer. I have added it now as this would keep the new in heap.
struct Node {
    int value;
    Node* left;
    Node* right;

     // Constructor
    Node(int value) : value(value), left(nullptr), right(nullptr) {}

    // Destructor
    ~Node() {
        delete left;
        delete right;
    }
};

// to create new node with given value
Node* newNode(const int& value) {
    return new Node(value);
}

//to create the tree as you mentioned
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


// this is te depth checking function.
// I have modified it as not trying to decrement anymore.
// The function is still the iterative version.
// rather than checking with if condition 
// Also I don't need a static variable as I am adding the results.
int maxDepth(Node* node) {
    //returning if you passed a null
    if (node == nullptr) {
        return 0;
    } else {
        // get left depth first and than right
        int leftDepth = maxDepth(node->left);
        int rightDepth = maxDepth(node->right);
        if (leftDepth > rightDepth) {
            return leftDepth + 1;
        } else {
            return rightDepth + 1;
        }
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

    delete root;
    return 0;
}