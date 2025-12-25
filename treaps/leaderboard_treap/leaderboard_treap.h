#pragma once
#include "treap.h"
#include "Leaderboard_playerID.h"
#include "Leaderboard_time.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

class leaderboard_treap {
public:
    treap<Leaderboard_time> time_Leaderboard;
    treap<Leaderboard_playerID> player_Times;

    leaderboard_treap(){}

    void registerTime(string userID, float newTime) {
        Leaderboard_playerID newEntryByPlayer(userID, newTime);
        Leaderboard_time     newEntryByTime(newTime, userID);

        // Check if the player already exists
        treap<Leaderboard_playerID>::Node* existingPlayerNode = player_Times.search(newEntryByPlayer);

        // Case: New Player (Node not found)
        if (existingPlayerNode == nullptr) {
            time_Leaderboard.insert(newEntryByTime);
            player_Times.insert(newEntryByPlayer);
            return;
        }

        
        float currentBestTime = existingPlayerNode->key.time;

        // If the new time is slower (or equal), we don't update the treap(s).
        if (newTime >= currentBestTime) {
            return;
        }

        // 4. Update the records
        // We reconstruct the old time object so we can remove it from the time_Leaderboard
        Leaderboard_time oldEntryByTime(currentBestTime, userID);

        time_Leaderboard.updateNode(oldEntryByTime, newEntryByTime);
        player_Times.updateNode(existingPlayerNode->key, newEntryByPlayer);
    }

    Leaderboard_time* getTop10() {
        return time_Leaderboard.getTopK(11);
    }
};


PYBIND11_MODULE(leaderboard_treap, m) {
     // defining the leaderboard time class variables as the getTop10 function returns a pointer to an array of Leaderboard_time objects
	pybind11::class_<Leaderboard_time>(m, "LeaderboardTime")
		.def_readwrite("time", &Leaderboard_time::time)
		.def_readwrite("userID", &Leaderboard_time::userID);

	pybind11::class_<leaderboard_treap>(m, "LeaderboardTreap")
		.def(pybind11::init<>())
		.def("registerTime", &leaderboard_treap::registerTime)
		.def("getTop10", &leaderboard_treap::getTop10);
}		