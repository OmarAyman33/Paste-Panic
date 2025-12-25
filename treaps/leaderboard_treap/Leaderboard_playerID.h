#pragma once
#include <string>
#include <iostream>

using namespace std;
class Leaderboard_playerID
{
public:
    string player_id;
    float time;

    // Constructors
    Leaderboard_playerID(string id, float t) : player_id(id), time(t) {}
    Leaderboard_playerID() : player_id(""), time(0) {}

    // --- Comparison Operator Overloads ---

    // Equality: Matches if IDs are the same (ignores time)
    bool operator==(const Leaderboard_playerID& other) const {
        return this->player_id == other.player_id;
    }

    // Inequality
    bool operator!=(const Leaderboard_playerID& other) const {
        return !(*this == other);
    }

    // Less Than: Alphabetical sort by ID only
    bool operator<(const Leaderboard_playerID& other) const {
        return this->player_id < other.player_id;
    }

    // Greater Than: Alphabetical sort by ID only
    bool operator>(const Leaderboard_playerID& other) const {
        return this->player_id > other.player_id;
    }

    // Less Than or Equal
    bool operator<=(const Leaderboard_playerID& other) const {
        return this->player_id <= other.player_id;
    }

    // Greater Than or Equal
    bool operator>=(const Leaderboard_playerID& other) const {
        return this->player_id >= other.player_id;
    }

    //// --- Output Stream Operator ---
    //friend std::ostream& operator<<(std::ostream& os, const Leaderboard_playerID& dt) {
    //    os << "[" << dt.player_id << ": " << dt.time << "s]";
    //    return os;
    //}
};