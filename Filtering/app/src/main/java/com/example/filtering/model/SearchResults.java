package com.example.filtering.model;

import java.util.ArrayList;

public class SearchResults {
    ArrayList<SearchResult> searchResults;
    boolean savedSearch;

    public SearchResults() {
        searchResults = new ArrayList<>();
    }

    public void emptyList() {
        searchResults = new ArrayList<>();
    }

    public void addElement(SearchResult element) {
        searchResults.add(element);
    }

    public void setSavedSearch(boolean savedSearch) {
        this.savedSearch = savedSearch;
    }

    public boolean getSavedSearch() {
        return this.savedSearch;
    }

    public ArrayList<SearchResult> getArrayList() {
        return searchResults;
    }

    public void setAllOld() {
        for(SearchResult s: searchResults) {
            s.setNewResult(false);
        }
    }
}
