"""Explicitly post-hoc, exact linear decomposition; no refitting or model selection."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from experiment import ROOT,RESULTS,prepare,save_json

def main():
    data=prepare();p=np.load(RESULTS/'ridge_parameters.npz');coefs=p['coef'].astype('float64')
    origins=data['idx']['test'];history=data['y'][origins[:,None]+np.arange(-144,0)]
    contrib=(history[:,None,:]-data['mean'])*coefs[None,:,:]
    intercept=data['std']*p['intercept'].astype('float64')+data['mean']
    reconstructed=contrib.sum(2)+intercept
    saved=pd.read_csv(RESULTS/'pred_ridge_s0.csv')[['pred_h1_GB','pred_h6_GB']].to_numpy()
    discrepancy=float(np.max(np.abs(reconstructed-saved)))
    assert discrepancy<.001
    pd.DataFrame({'lag_steps':np.arange(-144,0),'coefficient_h1':coefs[0],
                  'coefficient_h6':coefs[1]}).to_csv(RESULTS/'ridge_coefficients.csv',index=False)
    np.savez_compressed(RESULTS/'ridge_linear_contributions.npz',origins=origins,
                        contributions_GB=contrib,intercept_GB=intercept)
    save_json(RESULTS/'ridge_decomposition.json',{'status':'exploratory_post_hoc',
      'reference':'training mean volume','refitted':False,'max_reconstruction_discrepancy_GB':discrepancy,
      'last_lag_coefficient_h1':float(coefs[0,-1]),'last_lag_coefficient_h6':float(coefs[1,-1]),
      'intercept_GB':intercept.tolist(),
      'interpretation':'Exact fitted linear-model contribution relative to training mean; correlated lag coefficients are not causal importance.'})
    fig,axes=plt.subplots(1,2,figsize=(7,2.5))
    for j,ax in enumerate(axes):
        ax.plot(np.arange(-144,0),coefs[j],color='#2563a6',lw=1)
        ax.axhline(0,color='#aaa',lw=.5);ax.set(title=f'Horizon {[10,60][j]} min',
          xlabel='Lag (10-minute steps; -1 is most recent)',ylabel='Fitted linear coefficient')
        ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();(ROOT/'figures').mkdir(exist_ok=True);fig.savefig(ROOT/'figures/ridge_coefficients.png',dpi=180);plt.close(fig)
    print('Exploratory Ridge decomposition; maximum reconstruction discrepancy:',discrepancy,'GB')

if __name__=='__main__':main()
