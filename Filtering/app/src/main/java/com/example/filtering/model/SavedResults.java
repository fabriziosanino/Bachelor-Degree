package com.example.filtering.model;

import java.util.ArrayList;

public class SavedResults {
    ArrayList<SavedResult> savedResults;

    public SavedResults() {
        savedResults = new ArrayList<>();
    }

    public void emptyList() {
        savedResults = new ArrayList<>();
    }

    public void addElement(SavedResult element) {
        savedResults.add(element);
    }

    public ArrayList<SavedResult> getArrayList() {
        return savedResults;
    }
}
