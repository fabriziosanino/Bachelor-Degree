package com.example.filtering.viewModel;

import androidx.lifecycle.MutableLiveData;

import org.json.JSONArray;

public class DeleteResearchLiveData extends MutableLiveData<JSONArray> {
    public void updateDeleteResearch(JSONArray result) {postValue(result);}
}
