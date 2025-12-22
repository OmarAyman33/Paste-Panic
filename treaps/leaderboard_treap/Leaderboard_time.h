#pragma once
#include <string>
#include <iostream>

using namespace std;

class Leaderboard_time
{
public:
    float time;
    string player_id;

    // Constructors
    Leaderboard_time(float t, string id) : time(t), player_id(id) {}

    // Comparison Operator Overloads 

    // Equality: Both time and ID must be the same
    bool operator==(const Leaderboard_time& other) const {
        return (this->time == other.time) && (this->player_id == other.player_id);
    }


    bool operator!=(const Leaderboard_time& other) const {
        return !(*this == other);
    }

    // Less Than: Primary check on time, secondary check on ID
    bool operator<(const Leaderboard_time& other) const {
        if (this->time != other.time) {
            return this->time < other.time;
        }
        return this->player_id < other.player_id;
    }

    // Greater Than: Primary check on time, secondary check on ID
    bool operator>(const Leaderboard_time& other) const {
        if (this->time != other.time) {
            return this->time > other.time;
        }
        return this->player_id > other.player_id;
    }

    bool operator<=(const Leaderboard_time& other) const {
        return (*this < other) || (*this == other);
    }

    bool operator>=(const Leaderboard_time& other) const {
        return (*this > other) || (*this == other);
    }

    //// --- Optional: Output Stream Operator ---
    //// Useful for printing the tree later (e.g., cout << node->key)
    //friend std::ostream& operator<<(std::ostream& os, const Leaderboard_time& dt) {
    //    os << "[" << dt.time << "s - " << dt.player_id << "]";
    //    return os;
    //}
};