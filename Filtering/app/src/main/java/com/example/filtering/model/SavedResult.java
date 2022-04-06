package com.example.filtering.model;

import java.util.ArrayList;

public class SavedResult {
    private int id;
    private String researchName;
    private int elementNum;
    private ArrayList<String> images;

    public SavedResult(int id, String researchName, int elementNum, ArrayList<String> images) {
        this.id = id;
        this.researchName = researchName;
        this.elementNum = elementNum;
        this.images = images;
    }

    public String getResearchName() {
        return researchName;
    }

    public void setResearchName(String researchName) {
        this.researchName = researchName;
    }

    public int getElementNum() {
        return elementNum;
    }

    public void setElementNum(int elementNum) {
        this.elementNum = elementNum;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public ArrayList<String> getImages() {
        return images;
    }

    public void setImages(ArrayList<String> images) {
        this.images = images;
    }
}
