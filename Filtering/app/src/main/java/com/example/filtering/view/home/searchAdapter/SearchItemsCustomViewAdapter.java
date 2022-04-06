package com.example.filtering.view.home.searchAdapter;

import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
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
import androidx.recyclerview.widget.DiffUtil;
import androidx.recyclerview.widget.RecyclerView;

import com.example.filtering.R;
import com.example.filtering.model.SearchResult;
import com.example.filtering.viewModel.NetworkViewModel;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.InputStream;
import java.util.List;

public class SearchItemsCustomViewAdapter extends RecyclerView.Adapter<SearchItemsCustomViewAdapter.ViewHolder>{
    private List<SearchResult> mData;
    private LayoutInflater mIflater;
    private NetworkViewModel networkViewModel;
    //public ProgressDialog progressDialog;
    private Context context;

    public SearchItemsCustomViewAdapter(Context context, List<SearchResult> data, NetworkViewModel networkViewModel) {
        this.mIflater = LayoutInflater.from(context);
        this.mData = data;
        this.networkViewModel = networkViewModel;
        this.context = context;
    }

    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = mIflater.inflate(R.layout.search_list_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        SearchResult item = mData.get(position);
        if(item != null) {
            new DownloadImageTask(holder.img).execute(item.getProductImg());
            holder.txtName.setText(item.getProductName());
            holder.txtName.setOnClickListener(view -> {
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(item.getProductLink()));
                context.startActivity(intent);
            });

            if(item.getPrice().equals("0"))
                holder.txtPrice.setText("NO PRICE FOUND");
            else
                holder.txtPrice.setText("$" + item.getPrice());

            holder.btnClassify.setOnClickListener(view -> {
                JSONObject jsonObject = new JSONObject();
                try {
                    jsonObject.put("link", item.getProductLink());
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                networkViewModel.setProgressDialogMessage("Searching for reviews ... Please wait");
                networkViewModel.getProgressDialog().show();
                networkViewModel.classifyProduct(jsonObject);
            });

            holder.ok.setOnClickListener(view -> {
                openAlertDialog("Reliability between 100% and 71%");
            });

            holder.danger.setOnClickListener(view -> {
                openAlertDialog("Reliability less than 40%");
            });

            holder.warining.setOnClickListener(view -> {
                openAlertDialog("Reliability between 70% and 40% ");
            });

            if(item.isNewResult())
                holder.txtNew.setVisibility(View.VISIBLE);
            else
                holder.txtNew.setVisibility(View.INVISIBLE);

            if(item.getReliability() <= 40) {
                holder.danger.setVisibility(View.VISIBLE);
                holder.warining.setVisibility(View.INVISIBLE);
                holder.ok.setVisibility(View.INVISIBLE);
            } else if(item.getReliability() <= 70 && item.getReliability() > 40) {
                holder.warining.setVisibility(View.VISIBLE);
                holder.danger.setVisibility(View.INVISIBLE);
                holder.ok.setVisibility(View.INVISIBLE);
            } else {
                holder.ok.setVisibility(View.VISIBLE);
                holder.warining.setVisibility(View.INVISIBLE);
                holder.danger.setVisibility(View.INVISIBLE);
            }
        }
    }

    @Override
    public int getItemCount() {
        return mData.size();
    }

    public class  ViewHolder extends RecyclerView.ViewHolder implements AdapterView.OnItemSelectedListener {
        TextView txtName;
        ImageView img;
        ImageView warining;
        ImageView danger;
        ImageView ok;
        TextView txtPrice;
        Button btnClassify;
        TextView txtNew;

        ViewHolder(View itemView) {
            super(itemView);
            txtName = itemView.findViewById(R.id.txtName);
            img = itemView.findViewById(R.id.img);
            warining = itemView.findViewById(R.id.warning);
            ok = itemView.findViewById(R.id.ok);
            danger = itemView.findViewById(R.id.danger);
            txtPrice = itemView.findViewById(R.id.txtPrice);
            btnClassify = itemView.findViewById(R.id.btnClassify);
            txtNew = itemView.findViewById(R.id.txtNew);
        }

        @Override
        public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
            //Auto-generated method stub
        }

        public void onNothingSelected(AdapterView<?> arg0) {
            //Auto-generated method stub
        }
    }

    public void setData(List<SearchResult> newData) {
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
        private final List<SearchResult> oldPosts, newPosts;

        public PostDiffCallback(List<SearchResult> oldPosts, List<SearchResult> newPosts){
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
            return (oldPosts.get(oldItemPosition).getProductName().equals(newPosts.get(newItemPosition).getProductName()) && oldPosts.get(oldItemPosition).getProductLink().equals(newPosts.get(newItemPosition).getProductLink()) && (oldPosts.get(oldItemPosition).isNewResult() && !newPosts.get(newItemPosition).isNewResult()));
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
}
