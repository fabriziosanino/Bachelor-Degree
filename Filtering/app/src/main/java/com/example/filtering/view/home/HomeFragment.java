package com.example.filtering.view.home;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.ProgressDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.example.filtering.model.SearchResult;
import com.example.filtering.databinding.FragmentHomeBinding;
import com.example.filtering.view.home.searchAdapter.SearchItemsCustomViewAdapter;
import com.example.filtering.viewModel.NetworkViewModel;
import com.google.android.material.snackbar.Snackbar;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;

public class HomeFragment extends Fragment {

    private FragmentHomeBinding binding;
    NetworkViewModel networkViewModel;
    SearchItemsCustomViewAdapter adapter;

    ArrayList<SearchResult> searchResults;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {

        binding = FragmentHomeBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        networkViewModel = new ViewModelProvider(requireActivity()).get(NetworkViewModel.class);

        RecyclerView recyclerView = binding.lstItemsSearched;
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new SearchItemsCustomViewAdapter(getContext(), new ArrayList<>(), networkViewModel);
        recyclerView.setAdapter(adapter);

        networkViewModel.setProgressDialog(new ProgressDialog(getContext()));
        networkViewModel.setAdapterResearch(adapter);

        networkViewModel.getSaveResearchLiveData().observe(getViewLifecycleOwner(), result -> {
            try {
                networkViewModel.getProgressDialog().hide();

                JSONObject res = result.getJSONObject(0);

                if(res.getBoolean("error"))
                    openAlertDialog(res.getString("errorDescription"));
                else
                    openAlertDialog("Search saved successfully!");
            } catch (JSONException e) {
                e.printStackTrace();
            }
        });

        networkViewModel.getClassifyLiveData().observe(getViewLifecycleOwner(), result -> {
            try {
                networkViewModel.getProgressDialog().hide();

                JSONObject res = result.getJSONObject(0);

                if(res.getBoolean("error"))
                    openAlertDialog(res.getString("errorDescription"));
                else {
                    float positive = res.getInt("positive");
                    float negative = res.getInt("negative");
                    float neutral = res.getInt("neutral");

                    float tot = positive + negative + neutral;

                    if(positive != 0)
                        positive = (positive/tot) * 100;

                    if(negative != 0)
                        negative = (negative/tot) * 100;

                    if(neutral != 0)
                        neutral = (neutral/tot) * 100;

                    openAlertDialog("Positive: " + positive + "%\nNegative: " + negative + "%\nNeutral: " + neutral + "%");
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        });

        networkViewModel.getResearchDetailsLiveData().observe(getViewLifecycleOwner(), result -> {
            networkViewModel.getProgressDialog().hide();

            try {
                if (result.getBoolean("error")) {
                    openAlertDialog(result.getString("errorDescription"));
                } else {
                    changeVisibility(false);

                    binding.btnSave.setVisibility(View.INVISIBLE);
                    binding.btnBack.setVisibility(View.INVISIBLE);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        });

        networkViewModel.getProductsLiveData().observe(getViewLifecycleOwner(), result -> {
            try {
                if (result.getBoolean("error")) {
                    // LA RICERCA NON HA PRODOTTO ALCUN RISULTATO
                    changeVisibility(true);
                    openAlertDialog(result.getString("errorDescription"));

                    binding.btnSave.setVisibility(View.INVISIBLE);

                    networkViewModel.getProgressDialog().hide();
                    networkViewModel.getProgressBar().setVisibility(View.INVISIBLE);
                } else {
                    // LA RICERCA HA PRODOTTO DEI RISULTATI
                    String analyzedItems = result.getString("analyzed");
                    String foundItems = result.getString("found");

                    Snackbar.make(getView(), analyzedItems + foundItems, Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();

                    if(result.getBoolean("progressBar")) {
                        networkViewModel.getProgressBar().setVisibility(View.VISIBLE);
                        networkViewModel.getProgressDialog().hide();
                    } else {
                        networkViewModel.getProgressDialog().hide();
                        networkViewModel.getProgressBar().setVisibility(View.INVISIBLE);
                    }
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        });

        binding.btnFilter.setOnClickListener(view -> {
            //TODO: ELIMINARE CARICAMENTO QUANDO SI TORNA INDIETRO MENTRE STA ANCORA SCARICANDO PRODOTTI
            String productName = binding.inputName.getText().toString();
            productName = productName.replace(", ", ",");
            //productCharateristics = binding.inputCharacteristics.getText().toString();

            //ALMENO UNO DEI DUE FILTRI DEVE ESSERE COMPILATO
            if (!(/*productCharateristics.equals("") &&*/ productName.equals(""))) {

                InputMethodManager inputMethodManager = (InputMethodManager) getActivity().getSystemService(Activity.INPUT_METHOD_SERVICE);
                if (inputMethodManager.isAcceptingText()) {
                    inputMethodManager.hideSoftInputFromWindow(getActivity().getCurrentFocus().getWindowToken(), 0);
                }

                changeVisibility(false);
                networkViewModel.setProgressDialogMessage("Product search in progress. Wait for...");
                networkViewModel.getProgressDialog().show();
                try {
                    sendRequest(productName, true, false,  false);
                } catch (JSONException e) {
                    e.printStackTrace();
                    networkViewModel.getProgressDialog().dismiss();
                }
            } else {
                changeVisibility(true);

                openAlertDialog("Insert at least one filter");
            }
        });

        binding.btnBack.setOnClickListener(view -> {
            networkViewModel.getProgressBar().setVisibility(View.INVISIBLE);
            changeVisibility(true);
        });

        binding.infoName.setOnClickListener(view -> openAlertDialog("Insert the article to be searched by putting, divided by a comma, the characteristics that the product must have. " +
                "If possible, insert the units of measurement with space (e.g. 16 cm). For example if you need to search for an ASUS NOTEBOOK with 16 GB of RAM write 'ASUS NOTEBOOK, 16 GB RAM'"));

        /*binding.infoCharacteristics.setOnClickListener(view -> {
            openAlertDialog("In questo campo inserire le caratteristiche del prodotto. Non devono essere inserite frasi ma solo specifiche. Ad esempio se è necessario cercare un PC " +
                    "inserire tutte le specifiche necessarie (RAM 4Gb Intel Core i7)");
        });*/

        binding.btnFindMore.setOnClickListener(view -> {
            /* Nuovi risultati */ /* Toglierlo ne caso arrivi da saved search*/
            try {
                networkViewModel.getProgressBar().setVisibility(View.VISIBLE);
                sendRequest(networkViewModel.getProductName(), false, true, true);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        });

        binding.btnSave.setOnClickListener(view -> {
            if(searchResults.size() != 0) {
                JSONObject research = new JSONObject();
                try {
                    research.put("nameResearch", binding.inputName.getText());
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                JSONArray jsonArray = new JSONArray();

                for(SearchResult s: searchResults) {
                    JSONObject jsonObject = new JSONObject();
                    try {
                        jsonObject.put("productName", s.getProductName());
                        jsonObject.put("productLink", s.getProductLink());
                        jsonObject.put("productImg", s.getProductImg());
                        jsonObject.put("reliability", s.getReliability());
                        jsonObject.put("price", s.getPrice());

                        jsonArray.put(jsonObject);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }

                try {
                    research.put("products", jsonArray);
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                networkViewModel.setProgressDialogMessage("Saving the search in progress. Wait for...");
                networkViewModel.getProgressDialog().show();
                networkViewModel.saveResearch(research);
            } else
                openAlertDialog("Impossible to save. No products found!");
        });

        return root;
    }

    private void openAlertDialog(String message) {
        new AlertDialog.Builder(getContext())
                .setMessage(message)
                .setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialogInterface, int i) {
                        dialogInterface.dismiss();
                    }
                })
                .show();
    }

    private void sendRequest(String productName, boolean firstRequest, boolean findMore, boolean firstTimeFindMore) throws JSONException {
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("keywordName", productName);
        //jsonObject.put("keywordCharateristics", productCharateristics);
        jsonObject.put("startIndex", 0);
        jsonObject.put("firstRequest", firstRequest);
        jsonObject.put("findMore", findMore);

        networkViewModel.serachProducts(jsonObject, productName, firstTimeFindMore);
    }

    private void changeVisibility(boolean visibility) {
        if (visibility) {
            binding.btnFilter.setVisibility(View.VISIBLE);
            //binding.inputCharacteristics.setVisibility(View.VISIBLE);
            binding.inputName.setVisibility(View.VISIBLE);
            binding.txtArticleName.setVisibility(View.VISIBLE);
            //binding.txtCharacteristics.setVisibility(View.VISIBLE);
            binding.infoName.setVisibility(View.VISIBLE);
            //binding.infoCharacteristics.setVisibility(View.VISIBLE);

            binding.lstItemsSearched.setVisibility(View.INVISIBLE);
            binding.btnBack.setVisibility(View.INVISIBLE);
            binding.btnSave.setVisibility(View.INVISIBLE);
            binding.btnFindMore.setVisibility(View.INVISIBLE);
        } else {
            binding.btnFilter.setVisibility(View.INVISIBLE);
            //binding.inputCharacteristics.setVisibility(View.INVISIBLE);
            binding.inputName.setVisibility(View.INVISIBLE);
            binding.txtArticleName.setVisibility(View.INVISIBLE);
            //binding.txtCharacteristics.setVisibility(View.INVISIBLE);
            binding.infoName.setVisibility(View.INVISIBLE);
            //binding.infoCharacteristics.setVisibility(View.INVISIBLE);

            binding.lstItemsSearched.setVisibility(View.VISIBLE);
            binding.btnBack.setVisibility(View.VISIBLE);
            binding.btnSave.setVisibility(View.VISIBLE);
            binding.btnFindMore.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}