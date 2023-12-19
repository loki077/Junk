#include <iostream> 
#include <vector> 
#include <unordered_map> 

class Solution {
public:
    std::vector<int> twoSum(std::vector<int>& nums, int target) {
        std::unordered_map<int, int> prev_map; 

        for (int i = 0; i < nums.size(); ++i) {
            int diff = target - nums[i]; 
            std::cout << "target " << i << std::endl;

            if (prev_map.find(diff) != prev_map.end()) {
                return {prev_map[diff], i};
            }
            std::cout << i << std::endl;
            prev_map[nums[i]] = i;

            // Print the unordered_map
            for (const auto& pair : prev_map) {
                std::cout << "Key: " << pair.first << " Value: " << pair.second << std::endl;
            }
        }
        return {};
    }
};

int main() {
    // Create a vector of integers
    std::vector<int> nums = {2, 7, 11, 15};
    // Create an integer target
    int target = 13;

    // Create an object of the class Solution
    Solution sol;
    // Call the twoSum function on the object sol and print the result
    std::vector<int> result = sol.twoSum(nums, target);
    std::cout << "[" << result[0] << " " << result[1] << "]" << std::endl;

    return 0;
}