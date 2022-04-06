package com.example.filtering.viewModel;

import androidx.lifecycle.MutableLiveData;

import org.json.JSONArray;

public class ClassifyLiveData extends MutableLiveData<JSONArray> {
    public void updateClassify(JSONArray result) {postValue(result);}
}
