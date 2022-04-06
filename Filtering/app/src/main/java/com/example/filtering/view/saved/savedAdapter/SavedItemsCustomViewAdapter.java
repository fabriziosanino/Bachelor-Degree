package com.example.filtering.view.saved.savedAdapter;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.navigation.fragment.NavHostFragment;
import androidx.recyclerview.widget.DiffUtil;
import androidx.recyclerview.widget.RecyclerView;

import com.example.filtering.R;
import com.example.filtering.model.SavedResult;
import com.example.filtering.view.saved.SavedFragment;
import com.example.filtering.viewModel.NetworkViewModel;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.InputStream;
import java.util.List;

public class SavedItemsCustomViewAdapter extends RecyclerView.Adapter<SavedItemsCustomViewAdapter.ViewHolder>{
    private List<SavedResult> mData;
    private LayoutInflater mIflater;
    private NetworkViewModel networkViewModel;
    private SavedFragment fragmentPointer;
    private Context context;

        public SavedItemsCustomViewAdapter(Context context, List<SavedResult> data, NetworkViewModel networkViewModel, SavedFragment fragmentPointer) {
        this.mIflater = LayoutInflater.from(context);
        this.mData = data;
        this.networkViewModel = networkViewModel;
        this.context = context;
        this.fragmentPointer = fragmentPointer;
    }

    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = mIflater.inflate(R.layout.saved_list_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        SavedResult item = mData.get(position);
        if(item != null) {
            holder.txtResearchName.setText(item.getResearchName());
            holder.txtElementNum.setText(String.valueOf(item.getElementNum()));

            if(item.getElementNum() == 1) {
                new SavedItemsCustomViewAdapter.DownloadImageTask(holder.imgCenter).execute(item.getImages().get(0));
                holder.txtElementNum.setText(item.getElementNum() + " prodotto");
                holder.imgLeft.setVisibility(View.INVISIBLE);
                holder.imgRight.setVisibility(View.INVISIBLE);
            } else if(item.getElementNum() == 2) {
                new SavedItemsCustomViewAdapter.DownloadImageTask(holder.imgLeft).execute(item.getImages().get(0));
                new SavedItemsCustomViewAdapter.DownloadImageTask(holder.imgRight).execute(item.getImages().get(1));
                holder.imgCenter.setVisibility(View.INVISIBLE);
                holder.txtElementNum.setText(item.getElementNum() + " prodotti");
            } else {
                new SavedItemsCustomViewAdapter.DownloadImageTask(holder.imgLeft).execute(item.getImages().get(0));
                new SavedItemsCustomViewAdapter.DownloadImageTask(holder.imgRight).execute(item.getImages().get(1));
                new SavedItemsCustomViewAdapter.DownloadImageTask(holder.imgCenter).execute(item.getImages().get(2));
                holder.txtElementNum.setText(item.getElementNum() + " prodotti");
            }

            holder.btnShow.setOnClickListener(view -> {
                networkViewModel.setProgressDialogMessage("Search download in progress. Wait for...");
                networkViewModel.getProgressDialog().show();

                JSONObject jsonObject = new JSONObject();
                try {
                    jsonObject.put("idResearch", item.getId());
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                networkViewModel.findResearchDetails(jsonObject);

                /*TODO: NASCONDERE IL CARICAMENTO NELLA HOME PAGE QUANO SONO ARRIVATI I DATI*/
                //networkViewModel.getProgressDialog().hide();

                NavHostFragment.findNavController(fragmentPointer)
                        .navigate(R.id.action_nav_saved_to_nav_home);
            });

            networkViewModel.getDeleteResearchLiveData().observe(fragmentPointer.getViewLifecycleOwner(), result -> {
                try {
                    if (result.getJSONObject(0).getBoolean("error")) {
                        openAlertDialog(result.getJSONObject(0).getString("errorDescription"));
                    } else {
                        networkViewModel.getProgressDialog().hide();
                        openAlertDialog("Search successfully deleted!");
                        mData.remove(position);
                    }
                } catch(JSONException e) {
                    e.printStackTrace();
                }
            });

            holder.btnDelete.setOnClickListener(view -> {
                networkViewModel.setProgressDialogMessage("Search deletion in progress. Wait for...");
                networkViewModel.getProgressDialog().show();

                JSONObject jsonObject = new JSONObject();
                try {
                    jsonObject.put("idResearch", item.getId());
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                networkViewModel.deleteResearch(jsonObject);
            });
        }
    }

    private void openAlertDialog(String message) {
        new AlertDialog.Builder(context)
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
    public int getItemCount() {
        return mData.size();
    }

    public class  ViewHolder extends RecyclerView.ViewHolder implements AdapterView.OnItemSelectedListener {
        TextView txtResearchName;
        TextView txtElementNum;
        Button btnShow;
        Button btnDelete;
        ImageView imgLeft;
        ImageView imgRight;
        ImageView imgCenter;

        ViewHolder(View itemView) {
            super(itemView);
            txtResearchName = itemView.findViewById(R.id.txtResearchName);
            txtElementNum = itemView.findViewById(R.id.txtElementNum);
            btnShow = itemView.findViewById(R.id.btnShow);
            btnDelete = itemView.findViewById(R.id.btnDelete);
            imgCenter = itemView.findViewById(R.id.imgCenter);
            imgLeft = itemView.findViewById(R.id.imgLeft);
            imgRight = itemView.findViewById(R.id.imgRight);
        }

        @Override
        public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
            //Auto-generated method stub
        }

        public void onNothingSelected(AdapterView<?> arg0) {
            //Auto-generated method stub
        }
    }

    public void setData(List<SavedResult> newData) {
        if(mData != null) {
            PostDiffCallback postDiffCallback = new PostDiffCallback(mData, newData);
            DiffUtil.DiffResult diffResult = DiffUtil.calculateDiff(postDiffCallback);
            mData.clear();
            mData.addAll(newData);
            diffResult.dispatchUpdatesTo(this);
        } else {
            mData = newData;
        }
    }

    class PostDiffCallback extends DiffUtil.Callback {
        private final List<SavedResult> oldPosts, newPosts;

        public PostDiffCallback(List<SavedResult> oldPosts, List<SavedResult> newPosts){
            this.oldPosts = oldPosts;
            this.newPosts = newPosts;
        }

        @Override
        public int getOldListSize() {
            return oldPosts.size();
        }

        @Override
        public int getNewListSize() {
            return newPosts.size();
        }

        @Override
        public boolean areItemsTheSame(int oldItemPosition, int newItemPosition) {
            return (oldPosts.get(oldItemPosition).getResearchName().equals(newPosts.get(newItemPosition).getResearchName()));
        }

        @Override
        public boolean areContentsTheSame(int oldItemPosition, int newItemPosition) {
            return oldPosts.get(oldItemPosition).equals(newPosts.get(newItemPosition));
        }
    }

    //FUNZIONE CHE SCARICA IN BACKGROUND L'IMMAGINE DEL PRODOTTO E LA VISUALIZZA
    private class DownloadImageTask extends AsyncTask<String, Void, Bitmap> {
        ImageView bmImage;

        public DownloadImageTask(ImageView bmImage) {
            this.bmImage = bmImage;
        }

        protected Bitmap doInBackground(String... urls) {
            String urldisplay = urls[0];
            Bitmap mIcon11 = null;
            try {
                InputStream in = new java.net.URL(urldisplay).openStream();
                mIcon11 = BitmapFactory.decodeStream(in);
            } catch (Exception e) {
                Log.e("Error", e.getMessage());
                e.printStackTrace();
            }
            return mIcon11;
        }

        protected void onPostExecute(Bitmap result) {
            bmImage.setImageBitmap(result);
        }
    }
}
