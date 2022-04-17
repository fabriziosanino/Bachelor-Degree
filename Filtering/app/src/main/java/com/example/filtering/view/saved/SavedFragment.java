package com.example.filtering.view.saved;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.filtering.model.SavedResult;
import com.example.filtering.databinding.FragmentSavedBinding;
import com.example.filtering.view.saved.savedAdapter.SavedItemsCustomViewAdapter;
import com.example.filtering.viewModel.NetworkViewModel;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class SavedFragment extends Fragment {

    private FragmentSavedBinding binding;
    private NetworkViewModel networkViewModel;
    SavedItemsCustomViewAdapter adapter;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {

        binding = FragmentSavedBinding.inflate(inflater, container, false);
        View root = binding.getRoot();

        networkViewModel = new ViewModelProvider(requireActivity()).get(NetworkViewModel.class);

        RecyclerView recyclerView = binding.lstSavedReserches;
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
        adapter = new SavedItemsCustomViewAdapter(getContext(), new ArrayList<>(), networkViewModel, SavedFragment.this);
        recyclerView.setAdapter(adapter);

        networkViewModel.setAdapterSaved(adapter);

        networkViewModel.getReadResearchLiveData().observe(getViewLifecycleOwner(), result -> {
            if(result != null) {
                try {
                    networkViewModel.getProgressDialog().hide();

                    if (result.getBoolean("error")) {
                        openAlertDialog(result.getString("errorDescription"));
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                networkViewModel.getReadResearchLiveData().setValue(null);
            }
        });

        networkViewModel.getDeleteResearchLiveData().observe(getViewLifecycleOwner(), result -> {
            if(result != null) {
                try {
                    if (result.getJSONObject(0).getBoolean("error")) {
                        openAlertDialog(result.getJSONObject(0).getString("errorDescription"));
                    } else {
                        networkViewModel.getProgressDialog().hide();
                        openAlertDialog("Search successfully deleted!");
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                networkViewModel.getDeleteResearchLiveData().setValue(null);
            }
        });

        networkViewModel.setProgressDialogMessage("Downloading saved searches. Wait for...");
        networkViewModel.getProgressDialog().show();
        networkViewModel.readResearches();

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

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}