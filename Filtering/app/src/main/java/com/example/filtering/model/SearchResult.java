package com.example.filtering.model;

public class SearchResult {
    private String productName;
    private String productLink;
    private String productImg;
    private int reliability;
    private String price;
    private boolean newResult;

    public SearchResult(String productName, String productLink, String productImg, String price, int reliability, boolean newResult) {
        this.productName = productName;
        this.productLink = productLink;
        this.productImg = productImg;
        this.reliability = reliability;
        this.price = price;
        this.newResult = newResult;
    }

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public String getProductLink() {
        return productLink;
    }

    public void setProductLink(String productLink) {
        this.productLink = productLink;
    }

    public String getProductImg() {
        return productImg;
    }

    public void setProductImg(String productImg) {
        this.productImg = productImg;
    }

    public int getReliability() {
        return reliability;
    }

    public void setReliability(int reliability) {
        this.reliability = reliability;
    }

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public boolean isNewResult() {
        return newResult;
    }

    public void setNewResult(boolean newResult) {
        this.newResult = newResult;
    }
}
