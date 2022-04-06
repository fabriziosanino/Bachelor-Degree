package com.example.filtering.viewModel;

public class urls {
    private static final String serverUrlGetProducts = "http://10.0.2.2:5000/getProducts";
    private static final String serverUrlClassify = "http://10.0.2.2:5000/classifyReview";
    private static final String serverUrlSaveResearch = "http://10.0.2.2:5000/saveResearch";
    private static final String serverUrlReadResearches = "http://10.0.2.2:5000/readResearches";
    private static final String serverUrlGetResearchDetail = "http://10.0.2.2:5000/getResearchDetail";
    private static final String serverUrlDeleteResearch = "http://10.0.2.2:5000/deleteResearch";

    public static String getServerUrlGetProducts() {
        return serverUrlGetProducts;
    }

    public static String getServerUrlClassify() {
        return serverUrlClassify;
    }

    public static String getServerUrlSaveResearch() {
        return serverUrlSaveResearch;
    }

    public static String getServerUrlReadResearches() {
        return serverUrlReadResearches;
    }

    public static String getServerUrlGetResearchDetail() {
        return serverUrlGetResearchDetail;
    }

    public static String getServerUrlDeleteResearch() {
        return serverUrlDeleteResearch;
    }
}
