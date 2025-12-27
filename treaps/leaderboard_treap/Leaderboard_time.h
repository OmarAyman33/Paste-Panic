#pragma once
#include <string>
#include <iostream>

using namespace std;

class Leaderboard_time
{
public:
    float time;
    int wpm;
    string player_id;

    // Constructors
    Leaderboard_time(float t, int w, string id) : time(t), wpm(w), player_id(id) {}
    Leaderboard_time() : time(0), wpm(0), player_id("") {}
    // Comparison Operator Overloads 

    // Equality: Both time and ID must be the same
    bool operator==(const Leaderboard_time& other) const {
        return (this->wpm == other.wpm) && (this->player_id == other.player_id);
    }


    bool operator!=(const Leaderboard_time& other) const {
        return !(*this == other);
    }

    // Less Than: Primary check on WPM, secondary on Time, tertiary on ID
    bool operator<(const Leaderboard_time& other) const {
        if (this->wpm != other.wpm) {
            return this->wpm > other.wpm; // Higher WPM is "better" (comes first)
        }
        if (this->time != other.time) {
            return this->time < other.time; // Lower Time is "better"
        }
        return this->player_id < other.player_id;
    }

    // Greater Than: Primary check on WPM, secondary on Time, tertiary on ID
    bool operator>(const Leaderboard_time& other) const {
        if (this->wpm != other.wpm) {
            return this->wpm < other.wpm;
        }
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