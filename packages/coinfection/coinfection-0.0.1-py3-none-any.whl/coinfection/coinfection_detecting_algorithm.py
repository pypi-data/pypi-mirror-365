import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.lines as mlines
from typing import Callable, Iterable
import json
import itertools
import warnings
warnings.filterwarnings("ignore")

def visualize_cluster(data: pd.DataFrame, cluster_range: tuple[int,int], pad: int=20, ax=None, title:str="Selected cluster", log_yscale:bool=True, figsize:tuple[int,int]=(10,7),
                      outer_lines: float=None, pdf_pages: PdfPages=None, path: str=None, show: bool=True, close: bool=False, use_outer_lines_as_pad: bool=False, show_sgids: bool=False,
                      data_index_col: str='index', data_size_col: str='cell', data_sgid_col: str="sgid") -> None:
    '''
    Visualizes a cluster and the neighboring data points in a scatter plot.
    Args:
        data (pd.DataFrame): The DataFrame containing the data to visualize.
        cluster_range (tuple[int,int]): The range of indices to visualize as the cluster.
        pad (int): The number of indices to pad on both sides of the cluster.
        ax (matplotlib.axes.Axes): The axes to plot on. If None, a new figure and axes will be created.
        title (str): The title of the plot.
        log_yscale (bool): If True, the y-axis will be set to a logarithmic scale.
        figsize (tuple[int,int]): The size of the figure if a new figure is created. If an ax is given it will be ignored.
        outer_lines (float): If set, there will be arrows at the ends of the cluster range indicating a ratio.
        pdf_pages (PdfPages): If set, the figure will be saved to the PdfPages object.
        path (str): If set, the figure will be saved to the specified path.
        show (bool): If True, the figure will be shown.
        close (bool): If True, the figure will be closed after showing or saving.
        use_outer_lines_as_pad (bool): If True, the outer_lines will be used to calculate the pad instead of the pad parameter.
        show_sgids (bool): If True, the sgids/genes will be shown on the plot next to the points in the cluster.
        data_index_col (str): The name of the column in the DataFrame that contains the index of the data points.
        data_size_col (str): The name of the column in the DataFrame that contains the size of the data points.
        data_sgid_col (str): The name of the column in the DataFrame that contains the sgid/genes of the data points.
    '''

    # set minimum and maximum index
    if not use_outer_lines_as_pad:
        minimum_index = max(0, cluster_range[0]-pad)
        maximum_index = cluster_range[-1]+pad
    else:
        if outer_lines is None: raise ValueError("outer_lines should be specified when use_outer_lines_as_pad=True")
        maximum_size = outer_lines*data.loc[cluster_range[0], data_size_col]
        minimum_size = data.loc[cluster_range[-1], data_size_col]/outer_lines
        bigger_data = data[data[data_size_col]>maximum_size]
        smaller_data = data[data[data_size_col]<minimum_size]
        if bigger_data.shape[0] == 0:
            minimum_index = 0
        else:
            minimum_index = bigger_data.loc[0, data_index_col]
        if smaller_data.shape[0] == 0:
            maximum_index = data.shape[0]+1
        else:
            maximum_index = smaller_data.head(1)[data_index_col].values[0]
        
    # prep the data for visualization
    viz_data = data.iloc[minimum_index:maximum_index+1].copy()
    viz_data['category'] = viz_data[data_index_col].apply(lambda i: "cluster" if (i>=cluster_range[0] and i<=cluster_range[-1]) else "other")
    color_map = {"cluster": "#E39774", "other": "#326273"}
    colors = viz_data['category'].map(color_map)

    # create the plot
    given_ax = ax is not None
    if not given_ax:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None
    
    # visualize, title, labels, scale, legend
    ax.set_title(title)
    if log_yscale: ax.set_yscale("log")
    ax.scatter(viz_data[data_index_col], viz_data[data_size_col], c=colors)
    ax.set_xlabel("index")
    ax.set_ylabel("tumor size")
    ax.legend(handles=[mlines.Line2D([], [], color=color, marker='o', linestyle='', label=label) for label, color in color_map.items()])

    # show sgids    
    if show_sgids:
        max_size = max(viz_data[data_size_col])
        min_size = min(viz_data[data_size_col])
        
        size_range = max_size - min_size
        for _, row in viz_data.iterrows():
            if row['category'] == "other": continue

            if log_yscale:
                y_factor = 1.05 if row['index'] % 2 == 0 else 1/1.05
                y_pos = row[data_size_col] * y_factor
            else:
                y_mod = size_range/40 if row['index'] % 2 == 0 else -size_range/40
                y_pos = row[data_size_col] + y_mod
            plt.text(row[data_index_col], y_pos, row[data_sgid_col], ha='center', va='center', fontsize=8)

    # outer lines
    if outer_lines:
        max_index = cluster_range[0]
        min_index = cluster_range[-1]
        max_size = data[data_size_col].values[max_index]
        min_size = data[data_size_col].values[min_index]

        ax.arrow(max_index, max_size, 0, (max_size*outer_lines)-max_size, head_width=0.2, head_length=0.1, fc='black', ec='black')
        ax.arrow(min_index, min_size, 0, (min_size/outer_lines)-min_size, head_width=0.2, head_length=0.1, fc='black', ec='black')
        ax.text(max_index, (max_size+(max_size*outer_lines))/2, f"{int((outer_lines-1)*100)}%")

    # save, show, close
    if not given_ax:
        if pdf_pages is not None:
            pdf_pages.savefig(fig)
        if path is not None:
            fig.savefig(path, dpi=700)
        if show:
            fig.show()
        if close:
            plt.close(fig)
    else:
        if pdf_pages is not None or path is not None or show or close:
            print("Cannot save the plot to a file, PdfPages, show or close when ax is provided")

def echo(*values):
    '''
    Prints a progress, showing the current index and the total number of iterations.

    Args:
        *values: A list of values, like this: index, iterator, index, iterator, ...
    Example:
        echo(0, range(10), 1, range(20), 2, range(30))
    This will print something like:
        1/10 - 2/20 - 3/30
    The output ends with a carriage return, so it can be used in a loop to update the progress.
    '''
    pairs = list(zip(values[::2], values[1::2]))
    for it, (idx, iterator) in enumerate(pairs):
        length = len(iterator)
        print(f"{idx+1}/{length}", end='')
        if it != len(pairs) - 1:
            print(" - ", end='')
    print("\t\t\t\r", end='')

class CoinfectionDetectingAlgorithm:
    '''
    A class for detecting multiple infection events (coinfections) in a set of datasets from the same experiment.
    '''

    @staticmethod
    def _get_sizes_in_range(sizes: list, min_size: float, max_size: float) -> list:
        re = []
        for size in sizes:
            if size <= max_size:
                if size >= min_size:
                    re.append(size)
                else:
                    return re
        return re

    @staticmethod
    def _inner_p_value(ids: list, sizes: list, x: float, pcr_max_error: float=1.01, iterations: int=500, max_p_val:float=None, to_print:str=None) -> float:
        
        orig_max_size = sizes[min(ids)]
        orig_min_size = sizes[max(ids)]
        orig_ratio = max(orig_max_size / orig_min_size, pcr_max_error)
        n_of_tumors_in_cluster = len(ids)

        upper_size = min(orig_max_size*x, sizes[0])
        lower_size = max(orig_min_size/x, sizes[-1])

        sizes_in_range = CoinfectionDetectingAlgorithm._get_sizes_in_range(sizes, lower_size, upper_size)
        n_of_tumors_in_range = len(sizes_in_range)

        # p-value
        last_p_val = 0
        for iter_index in range(1, iterations+1):
            new_sizes = sorted(np.random.uniform(lower_size, upper_size, n_of_tumors_in_range), reverse=True)
            p_val = 0
            for i, big in enumerate(new_sizes[:n_of_tumors_in_range-n_of_tumors_in_cluster+1]):
                small = new_sizes[i+n_of_tumors_in_cluster-1]
                if (big/small) <= orig_ratio:
                    p_val = 1
                    break
            if iter_index == 1:
                last_p_val = p_val
            else:
                last_p_val = ((iter_index-1)*last_p_val+p_val)/iter_index
            
            # optimization
            if max_p_val:
                a = max_p_val*iterations
                b = (1-max_p_val)*iterations
                if iter_index >= a:
                    if last_p_val*iter_index >= a:
                        return last_p_val
                if iter_index >= b:
                    if iter_index*(1-last_p_val) >= b:
                        return last_p_val
                    
        return last_p_val

    @staticmethod
    def _outer_p_value(ids: list, sizes: list, x: float, iterations: int=500, max_p_val: float=None, to_print: str=None) -> float:
        
        orig_max_size = sizes[min(ids)]
        orig_min_size = sizes[max(ids)]
        if min(ids)==0 and max(ids)==len(sizes)-1:
            raise Exception("The whole sizes is one group")
        elif min(ids)==0:
            orig_ratio = orig_min_size/sizes[max(ids)+1]
        elif max(ids)==len(sizes)-1:
            orig_ratio = sizes[min(ids)-1]/orig_max_size
        else:
            orig_ratio = min(orig_min_size/sizes[max(ids)+1], sizes[min(ids)-1]/orig_max_size)

        upper_size = min(orig_max_size*x, sizes[0])
        lower_size = max(orig_min_size/x, sizes[-1])

        sizes_in_range = CoinfectionDetectingAlgorithm._get_sizes_in_range(sizes, lower_size, upper_size)
        n_of_tumors_in_range = len(sizes_in_range)

        # p-value
        last_p_val = 0
        for iter_index in range(1, iterations+1):
            new_sizes = sorted(np.random.uniform(lower_size, upper_size, n_of_tumors_in_range), reverse=True)

            p_val = 0
            for i, big in enumerate(new_sizes[:-1]):
                small = new_sizes[i+1]
                if (big/small) >= orig_ratio:
                    p_val = 1
                    break
            
            if iter_index == 1:
                last_p_val = p_val
            else:
                last_p_val = ((iter_index-1)*last_p_val+p_val)/iter_index
            
            # optimization
            if max_p_val:
                a = max_p_val*iterations
                b = (1-max_p_val)*iterations
                if iter_index >= a:
                    if last_p_val*iter_index >= a:
                        return last_p_val
                if iter_index >= b:
                    if iter_index*(1-last_p_val) >= b:
                        return last_p_val
                    
        return last_p_val

    @staticmethod
    def _get_all_possible_groups(from_to: tuple[int, int], max_group: int):
        indexes = np.arange(from_to[0], from_to[1]+1, 1)
        groups = []
        for idx1 in indexes:
            for idx2 in indexes[idx1+1:idx1+max_group]:
                groups.append(indexes[idx1:idx2+1])
        return pd.Series(groups)

    @staticmethod
    def _create_unions(groups: list[list[int]]) -> list[list[int]]:
        results = []
        for group in groups:
            if not results:
                results.append(group)
            else:
                last_group = results[-1]
                overlap = len(set(group).intersection(set(last_group))) > 0
                if overlap:
                    new_group = list(set(group+last_group))
                    results[-1] = new_group
                else:
                    results.append(group)
        return results

    @staticmethod
    def _get_type(group: list[int], unions: list[list[int]], groups: list[list[int]]) -> str:
        if group in unions:
            return "union"

        possible_types = []
        for other_group in groups:
            n_of_matches = 0
            n_of_mismatches = 0
            for g in group:
                if g in other_group:
                    n_of_matches += 1
                else:
                    n_of_mismatches += 1
            if n_of_mismatches == 0 and len(other_group)!=len(group):
                return "part_of_other_group"
            if n_of_matches > 0 and n_of_mismatches > 0:
                possible_types.append("overlap")
        if len(possible_types)==0 or not ("overlap" in possible_types):
            raise Exception("undefined type: ", group, unions, groups)
        else:
            return "overlap"
        
    @staticmethod
    def _get_list_from_str(string: str) -> list[int]:
        '''
        Transforms the saved list (string) in the csv back to a list
        ie: [ 0 1 2 3 ] -> [0,1,2,3] or [0 1 2   ] -> [0,1,2]
        '''

        # leading or trailing whitespace
        string = string.strip()

        # start and end of list
        if string[0] == '[':
            string = string[1:]
        else:
            raise Exception
        if string[-1] == ']':
            string = string[:-1]
        else:
            raise Exception
        
        # splitting
        splitted_string = string.split(" ")
        values = []
        for item in splitted_string:
            if item == " " or item == "":
                continue
            else:
                stripped_item = item.strip()
                values.append(int(stripped_item))
        return values

    @staticmethod
    def _maximum_accuracy_filtering(ids: list[int], sizes: list[float], maximum_accuracy: float) -> int:
        biggest_size = sizes[min(ids)]
        smallest_size = sizes[max(ids)]
        cluster_range = biggest_size/smallest_size
        if cluster_range > maximum_accuracy:
            return 1
        else:
            return 0

    @staticmethod
    def _minimum_accuracy_filtering(ids: list[int], sizes: list[float], minimum_accuracy: float) -> int:
        left = max(min(ids)-1, 0)
        right= min(max(ids)+1, len(sizes))
        left_size = sizes[left]
        right_size = sizes[right]
        cluster_range = left_size/right_size
        if cluster_range < minimum_accuracy:
            return 1
        else:
            return 0

    def _create_and_plot_metrics(self, gene_col: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        all_genes = set()
        for dataset in self.datasets.values():
            all_genes.update(set(dataset[gene_col].unique()))
        all_genes = list(all_genes)

        tumor_number_values = pd.DataFrame(columns=list(self.datasets.keys()), index=all_genes)
        percentile_values = pd.DataFrame(columns=list(self.datasets.keys()), index=all_genes)

        for dataset_id, dataset in self.datasets.items():

            size_cutoff = np.quantile(dataset[self.size_col].values, 0.95)
            tumor_number_norm = dataset[dataset[self.size_col] >= size_cutoff].shape[0]

            for gene in all_genes:
                try: percentile_value = np.quantile(dataset[dataset[gene_col]==gene][self.size_col].values, 0.95)
                except IndexError: percentile_value = 0
                percentile_values.loc[gene, dataset_id] = percentile_value/size_cutoff
                tumor_number_value = dataset[(dataset[gene_col]==gene) & (dataset[self.size_col]>size_cutoff)].shape[0]
                tumor_number_values.loc[gene, dataset_id] = tumor_number_value/tumor_number_norm
        metric_results = pd.DataFrame(columns=['percentile', 'tumor_number'], index=all_genes)
        metric_results['percentile'] = percentile_values.mean(axis=1)
        metric_results['tumor_number'] = tumor_number_values.mean(axis=1)

        plt.figure()
        sns.scatterplot(data=metric_results, x='percentile', y='tumor_number')
        plt.show()

        return metric_results, tumor_number_values, percentile_values

    def _get_weak_genes(self, metric_results: pd.DataFrame, tumor_number_threshold: float, percentile_threshold: float) -> list[str]:
        return metric_results[(metric_results['tumor_number'] < tumor_number_threshold) & (metric_results['percentile'] < percentile_threshold)].index.tolist()

    def _calculate_piggyback_score_change(self, weak_genes: list[str], gene_col: str, calc_pval: bool=False, iterations: int=1000, verbose: bool=True) -> tuple[int, int, list[int], float]:
        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters:
            print("ERROR:\tYou need to set the parameters with set_parameters() first")
            return
        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return
        
        full_score_before = 0
        full_score_after = 0
        to_select_by_dataset_id = {}

        groups = self.get_filtered_groups()

        for dataset_id, dataset in self.datasets.items():
            
            # original score
            orig_dataset = dataset.head(self.max_index)
            score_before = sum(self.max_index - orig_dataset[orig_dataset[gene_col].isin(weak_genes)]['index'])

            # without coinfections
            selected_groups = groups[groups['dataset_id']==dataset_id]
            to_select = sum(list(map(lambda ls: len(ls), list(selected_groups['ids'].values))))
            to_select_by_dataset_id[dataset_id] = to_select

            if to_select > 0:
                selected_ids = list(selected_groups['ids'].values)
                avoid_ids = [single_id for single_ids in selected_ids for single_id in single_ids]
            else:
                if verbose: print(f"Dataset {dataset_id}:\n\tSkipping, no groups found.")
                continue
            
            dataset_avoided = dataset[~dataset['index'].isin(avoid_ids)]
            dataset_avoided = dataset_avoided.head(self.max_index).reset_index(drop=True).reset_index()
            score_after = sum(self.max_index - dataset_avoided[dataset_avoided[gene_col].isin(weak_genes)]['level_0'])


            full_score_before += score_before
            full_score_after += score_after

            if verbose: print(f"Dataset {dataset_id}:\n\tScore before: {score_before}\n\tScore after: {score_after}")

        if calc_pval:
            new_ranks = []

            for iteration in range(iterations):
                if verbose: echo(iteration, range(iterations))

                full_score_after_iter = 0
                for dataset_id, dataset in self.datasets.items():
                    to_select = to_select_by_dataset_id[dataset_id]
                    if to_select == 0:
                        continue
                    
                    avoid_ids = list(np.random.choice(list(range(self.max_index)), size=to_select, replace=False))

                    dataset_avoided = dataset[~dataset['index'].isin(avoid_ids)]
                    dataset_avoided = dataset_avoided.head(self.max_index).reset_index(drop=True).reset_index()
                    score_after_iter = sum(self.max_index - dataset_avoided[dataset_avoided[gene_col].isin(weak_genes)]['level_0'])

                    full_score_after_iter += score_after_iter
                new_ranks.append(full_score_after_iter)
            pval = len(list(filter(lambda x: x<=full_score_after, new_ranks)))/len(new_ranks)
            print(f"Full score before: {full_score_before}, Full score after: {full_score_after}, p-value: {pval}")

            return full_score_before, full_score_after, new_ranks, pval
        else:
            return full_score_before, full_score_after, None, None

    @staticmethod
    def create_dict_from_dataframe(dataframe: pd.DataFrame, sample_col: str, size_col: str, gene_col: str=None) -> dict[str, pd.DataFrame]:
        '''
        Creates a dictionary from a single pandas DataFrame, where each key is a sample ID and the value is a DataFrame containing the data for that sample.
        The DataFrame is sorted by the size column in descending order and the index is reset.
        Args:
            dataframe (pd.DataFrame): The DataFrame to create the dictionary from. This should contain the data for multiple samples.
            sample_col (str): The name of the column in the DataFrame that contains the sample IDs.
            size_col (str): The name of the column in the DataFrame that contains the clone/tumor sizes.
            gene_col (str): The name of the column in the DataFrame that contains the gene/sgID/TS information. If None, it will not be included in the resulting DataFrame.
        Returns:
            datasets (dict[str, pd.DataFrame]): A dictionary where each key is a sample ID and the value is a DataFrame containing the data for that sample. These dataframes are sorted by the clone/tumor size in descending order.
        '''
        assert sample_col in dataframe.columns, f"ERROR:\t{sample_col} is not a column in the dataframe"
        assert size_col in dataframe.columns, f"ERROR:\t{size_col} is not a column in the dataframe"
        if gene_col is not None:
            assert gene_col in dataframe.columns, f"ERROR:\t{gene_col} is not a column in the dataframe"
        assert not "index" in dataframe.columns, "ERROR:\tThe dataframe should not have a column named 'index', it will be used as the index of the DataFrame"

        datasets = {}
        sample_ids = dataframe[sample_col].unique()
        for sample_id in sample_ids:
            data = dataframe[dataframe[sample_col]==sample_id]
            data = data.sort_values(size_col, ascending=False).reset_index(drop=True).reset_index()
            if gene_col is None:
                data = data[['index', size_col]]
            else:
                data = data[['index', gene_col, size_col]]
            datasets[sample_id] = data
        return datasets

    @staticmethod
    def create_dict_from_paths(paths: list[str], size_col: str, gene_col: str=None) -> dict[str, pd.DataFrame]:
        '''
        Creates a dictionary from a list of file paths, where each key is the file path and the value is a DataFrame containing the data from that file.
        The DataFrame is sorted by the size column in descending order and the index is reset.
        Args:
            paths (list[str]): A list of file paths to read the data from.
            size_col (str): The name of the column in the DataFrame that contains the clone/tumor sizes.
            gene_col (str): The name of the column in the DataFrame that contains the gene/sgid information. If None, it will not be included in the resulting DataFrame.
        Returns:
            datasets (dict[str, pd.DataFrame]): A dictionary where each key is a file path and the value is a DataFrame containing the data from that file.
        '''
        datasets = {}
        for path in paths:
            try:
                data = pd.read_csv(path)
            except:
                print(f"ERROR:\tCould not read {path}, skipping")
                continue
            data = data.sort_values(size_col, ascending=False).reset_index(drop=True).reset_index()
            if gene_col is None:
                data = data[['index', size_col]]
            else:
                data = data[['index', gene_col, size_col]]
            datasets[path] = data
        return datasets

    @staticmethod
    def get_approximate_max_indices(datasets: dict[str, pd.DataFrame], experimental_noise: float, max_group: int, size_col: str) -> list[int]:
        '''
        Finds the smallest index where the number of clones/tumors in experimental_noise range is greater than max_group for each dataset.
        Args:
            datasets (dict[str, pd.DataFrame]): A dictionary of pandas DataFrames. Each DataFrame is a different sample from the same experiment.
            experimental_noise (float): The experimental noise to consider when looking for the maximum index.
            max_group (int): The maximum number of clones/tumors in the same multiple infection event.
            size_col (str): The name of the column in the DataFrame that contains the clone/tumor sizes.
        Returns:
            max_indices (list[int]): A list of indices, one for each dataset, where the number of clones/tumors in the minimum_accuracy range is greater than max_group.
        '''
        max_indices = []
        exp_noise_half = 1+(experimental_noise-1)/2
        for orig_data in datasets.values():
            data = orig_data.copy()
            sizes = data[size_col].values
            data['num_close'] = data[size_col].apply(lambda size: sizes[(sizes<size*exp_noise_half) & (sizes>size/exp_noise_half)].shape[0])
            max_index = data[data['num_close']>max_group]['index'].values[0]
            max_indices.append(max_index)
        return list(map(int, max_indices))

    @staticmethod
    def create_sample_dataset(n_of_samples: int=10, coinfection_probability: float=0.3, coinfection_noise: float=1.05, random_state: int=42) -> pd.DataFrame:
        '''
        Creates a sample dataset for testing and showcasing the coinfection detecting algorithm.
        Args:
            n_of_samples (int): The number of samples to create.
            coinfection_probability (float): The probability of a clone/tumor being part of a multiple infection event.
            coinfection_noise (float): The noise factor applied to the clone/tumor sizes in the same multiple infection event, to simulate real-world experimental noise.
            random_state (int): The random state to use for reproducibility.
        Returns:
            sample_data (pd.DataFrame): A DataFrame containing the sample data with columns 'sample_id', 'size', and 'gene'.
        '''

        rng = np.random.default_rng(random_state)

        sample_data = pd.DataFrame(columns=['sample_id', 'size', 'gene'])

        for idx in range(n_of_samples):
            n_of_tumors = int(rng.uniform(1_000, 10_000))
            sizes = np.power(2, 1/(rng.normal(loc=0.14, scale=0.02494, size=n_of_tumors)))
            n_of_infections = rng.geometric(1-coinfection_probability, size=n_of_tumors)
            expanded_sizes = np.repeat(sizes, n_of_infections)
            noisy_sizes = expanded_sizes * np.exp(rng.uniform(np.log(1/coinfection_noise), np.log(coinfection_noise), size=expanded_sizes.shape[0]))

            genes = rng.choice([chr(65+i) for i in range(10)], size=noisy_sizes.shape[0])

            current_data = pd.DataFrame(columns=['sample_id', 'size', 'gene'])
            current_data['gene'] = genes
            current_data['size'] = noisy_sizes
            current_data['sample_id'] = f"sample_{idx}"

            sample_data = pd.concat([sample_data, current_data])


        return sample_data

    def __init__(self, 
                 datasets: dict[str,pd.DataFrame], 
                 max_group:int, 
                 max_index:int, 
                 range_parameters:list[float], 
                 max_p_vals:list[float], 
                 size_col:str, 
                 pcr_max_error:float=1.01,
                 iterations:int=250,
                 minimum_accuracy: float=None,
                 drop_with_minimum_accuracy:bool=False,
                 maximum_accuracy: float=None,
                 drop_with_maximum_accuracy:bool=False,
                 heuristic_filterings:Iterable[Callable[[Iterable[int], Iterable[float], float, float], int]]=None, 
                 drop_with_heuristic:bool=False
                 ) -> None:
        '''
        Args:
            datasets (dict[str,pd.DataFrame]): A dictionary of pandas DataFrames. Each DataFrame is a different sample from the same experiment. Those dataframes should be sorted by the clone/tumor size in descending order.
            max_group (int): The maximum number of clones/tumors in the same multiple infection event.
            max_index (int): The maximum index of the dataset to consider, indices above this will not be analyzed (but they will be used for p-value calculations).
            range_parameters (list[float]): A list of different parameter values for the range, used in the p-value calculations.
            max_p_vals (list[float]): A list of maximum p-values to consider for the p-value calculations.
            size_col (str): The name of the column in the DataFrame that contains the clone/tumor sizes.
            pcr_max_error (float): Used in the p-value calculations, clones/tumors with size ratio under this value are only possible by chance, so we consider their ratio as pcr_max_error.
            iterations (int): The number of iterations to run for the p-value calculations.
            minimum_accuracy (float): If set, the value will be calculated.
            drop_with_minimum_accuracy (bool): If set, multiple infection events where the neighboring clone/tumor size range is below the minimum_accuracy will be dropped. minimum_accuracy has to be set for this to work.
            maximum_accuracy (float): If set, the value will be calculated.
            drop_with_maximum_accuracy (bool): If set, multiple infection events where the size ratio is above the maximum_accuracy will be dropped. maximum_accuracy has to be set for this to work.
            heuristic_filterings (Iterable[Callable[[Iterable[int], Iterable[float], float, float], int]]): A list of heuristic filtering functions. Each function should take the ids of the multiple infection event, the sizes of the clones/tumors, the range value and the pcr_max_error as arguments and return 1 if the event should be dropped, 0 otherwise.
            drop_with_heuristic (bool): If set, multiple infection events where the heuristic filtering functions return 1 will be dropped. heuristic_filterings has to be set for this to work.
        '''
        
        self.datasets = datasets
        self.max_group = max_group
        self.max_index = max_index
        self.xs = range_parameters
        self.max_p_vals = max_p_vals
        self.size_col = size_col
        self.pcr_max_error = pcr_max_error
        self.iterations = iterations
        self.minimum_accuracy = minimum_accuracy
        self.drop_with_minimum_accuracy = drop_with_minimum_accuracy
        self.maximum_accuracy = maximum_accuracy
        self.drop_with_maximum_accuracy = drop_with_maximum_accuracy
        self.heuristic_filterings = heuristic_filterings
        self.drop_with_heuristic = drop_with_heuristic

        self.all_groups = pd.DataFrame()
        self.ran_p_val = False
        self.created_type_distributions = False
        self.selected_parameters = False

    def run_p_value_functions(self) -> None:
        '''
        Calculates the inner and outer p-values for all datasets and all possible groups of clones/tumors in each sample, then compiles the results into a single DataFrame.
        '''

        print("INFO:\tStarting p-value calculations.")
        for idx, (filename, data) in enumerate(self.datasets.items()):
            all_sizes = data[self.size_col].values
            filtered_data = data.head(self.max_index)
            sizes = filtered_data[self.size_col].values

            groups_df = pd.DataFrame()
            groups = self._get_all_possible_groups((0,len(sizes)-1), max_group=self.max_group)
            groups_df['ids'] = groups
            groups_df['short_id'] = groups_df['ids'].apply(lambda ids: f"{min(ids)}...{max(ids)}")

            if self.minimum_accuracy:
                groups_df['min_acc'] = groups_df['ids'].apply(lambda ids: self._minimum_accuracy_filtering(ids, all_sizes, self.minimum_accuracy))
                if self.drop_with_minimum_accuracy:
                    groups_df = groups_df[groups_df['min_acc']<1]
            if self.maximum_accuracy:
                groups_df['max_acc'] = groups_df['ids'].apply(lambda ids: self._maximum_accuracy_filtering(ids, all_sizes, self.maximum_accuracy))
                if self.drop_with_maximum_accuracy:
                    groups_df = groups_df[groups_df['max_acc']<1]

            for range_idx, x in enumerate(self.xs):
                echo(idx, self.datasets, range_idx, self.xs)
                
                if self.heuristic_filterings:
                    for hf_idx, heuristic_filtering in enumerate(self.heuristic_filterings):
                        groups_df[f"hf_{hf_idx}"] = groups_df['ids'].apply(lambda ids: heuristic_filtering(ids, all_sizes, x, self.pcr_max_error))
                    groups_df['max_hf'] = groups_df.apply(lambda row: max([row[f'hf_{i}'] for i in range(len(self.heuristic_filterings))]), axis=1)
                    if self.drop_with_heuristic:
                        groups_df = groups_df[groups_df['max_hf']<1]
                    
                groups_df[f'inner_{x}'] = groups_df['ids'].apply(lambda ids: self._inner_p_value(ids, all_sizes, x=x, pcr_max_error=self.pcr_max_error, iterations=self.iterations))
                groups_df[f'outer_{x}'] = groups_df['ids'].apply(lambda ids: self._outer_p_value(ids, all_sizes, x=x, iterations=self.iterations))
                groups_df[f'max_p_{x}'] = groups_df[[f'inner_{x}', f'outer_{x}']].max(axis=1)
                
            groups_df['dataset_id'] = filename
            self.all_groups = pd.concat([self.all_groups, groups_df])

        self.ran_p_val = True
        print("\nINFO:\tDone.")

    def save_p_value_calculations(self, path: str) -> None:
        '''
        Saves the p-value calculations to a .csv file and the metadata to a .json file.

        Args:
            path (str): The path to save the files. It should not include the file extension, it will be added automatically.
        '''

        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first")
            return
        if path.split(".")[-1] in ['csv']:
            print("ERROR:\tYou can't specify the file format")
            return
        
        data_path = f"{path}.csv"
        metadata_path = f"{path}_METADATA.json"

        metadata = {}
        metadata['max_group'] = self.max_group
        metadata['max_index'] = self.max_index
        metadata['xs'] = self.xs
        metadata['max_p_vals'] = self.max_p_vals
        metadata['pcr_max_error'] = self.pcr_max_error
        metadata['iterations'] = self.iterations
        metadata['minimum_accuracy'] = self.minimum_accuracy
        metadata['drop_with_minimum_accuracy'] = self.drop_with_minimum_accuracy
        metadata['maximum_accuracy'] = self.maximum_accuracy
        metadata['drop_with_maximum_accuracy'] = self.drop_with_maximum_accuracy
        metadata['drop_with_heuristic'] = self.drop_with_heuristic
        json_dict = json.dumps(metadata)

        print(f"Saving .csv (p value calculations) to: {data_path}")
        self.all_groups.to_csv(data_path, index=False)
        print(f"Saving .json (metadata) to: {metadata_path}")
        with open(metadata_path, "w") as f:
            f.write(json_dict)            

    def load_p_value_calculations(self, path_to_csv:str, path_to_json:str=None, overwrite:bool=False) -> None:
        '''
        Loads the p-value calculations from a .csv file and if set, checks the metadata from the .json file.

        Args:
            path_to_csv (str): The path to the .csv file containing the p-value calculations.
            path_to_json (str): The path to the .json file containing the metadata. If not set, the metadata will not be checked.
            overwrite (bool): If True, the existing all_groups DataFrame will be overwritten. If False, an error will be raised if all_groups is not empty.
        '''

        if self.all_groups.shape[0] != 0 and not overwrite:
            print("ERROR:\tall_groups is not empty and overwrite is set to False")
            return
        else:
            if path_to_json:
                with open(path_to_json, "r") as f:
                    metadata = json.loads(f.read())
                assert metadata['max_group'] == self.max_group, "ERROR:\tmax_group in metadata does not match the one in the class"
                assert metadata['max_index'] == self.max_index, "ERROR:\tmax_index in metadata does not match the one in the class"
                assert metadata['xs'] == self.xs, "ERROR:\txs in metadata does not match the one in the class"
                assert metadata['max_p_vals'] == self.max_p_vals, "ERROR:\tmax_p_vals in metadata does not match the one in the class"
                assert metadata['pcr_max_error'] == self.pcr_max_error, "ERROR:\tpcr_max_error in metadata does not match the one in the class"
                assert metadata['iterations'] == self.iterations, "ERROR:\titerations in metadata does not match the one in the class"
                assert metadata['minimum_accuracy'] == self.minimum_accuracy, "ERROR:\tminimum_accuracy in metadata does not match the one in the class"
                assert metadata['drop_with_minimum_accuracy'] == self.drop_with_minimum_accuracy, "ERROR:\tdrop_with_minimum_accuracy in metadata does not match the one in the class"
                assert metadata['maximum_accuracy'] == self.maximum_accuracy, "ERROR:\tmaximum_accuracy in metadata does not match the one in the class"
                assert metadata['drop_with_maximum_accuracy'] == self.drop_with_maximum_accuracy, "ERROR:\tdrop_with_maximum_accuracy in metadata does not match the one in the class"
                assert metadata['drop_with_heuristic'] == self.drop_with_heuristic, "ERROR:\tdrop_with_heuristic in metadata does not match the one in the class"
                print("INFO:\tMetadata loaded and checked successfully.")

            csv = pd.read_csv(path_to_csv)
            if "Unnamed: 0" in csv.columns:
                csv = csv.drop("Unnamed: 0", axis=1)
            csv['list_ids'] = csv['ids'].apply(self._get_list_from_str)
            csv = csv.drop("ids", axis=1)
            csv = csv.rename(columns={"list_ids": "ids"})

            dataset_ids = csv['dataset_id'].unique()
            all_present = all([dataset_id in self.datasets.keys() for dataset_id in dataset_ids])
            if all_present:
                self.all_groups = csv
                self.ran_p_val = True
            else:
                print("ERROR:\tNot all dataset_ids in the csv are present in the datasets dictionary")

    def create_type_distributions(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        '''
        This function creates a DataFrame containing the counts of different types of multiple infection events (union, part_of_other_group, overlap) for each combination of range and maximum p-value.
        '''

        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first")
            return

        self.counts = pd.DataFrame(columns=['max_p', 'x', 'union', 'part_of_other_group', 'overlap'])
        self.filtered_groups = {x: {} for x in self.xs}

        for max_p in self.max_p_vals:
            for x in self.xs:

                type_counter = {'max_p': max_p, 'x': x, 'union': 0, 'part_of_other_group': 0, 'overlap': 0}
                all_filtered = pd.DataFrame()
                
                for dataset_id in self.all_groups['dataset_id'].unique():
                    groups = self.all_groups[self.all_groups['dataset_id']==dataset_id]
                    filtered = groups[groups[f'max_p_{x}']<max_p].copy()

                    list_groups = [list(ids) for ids in filtered['ids'].values]
                    unions = self._create_unions(list_groups)
                    filtered['type'] = filtered['ids'].apply(lambda ids: self._get_type(list(ids), unions, list_groups))
                    all_filtered = pd.concat([all_filtered, filtered], axis=0)

                for key, value in all_filtered['type'].value_counts().to_dict().items():
                    type_counter[key] += value
                self.filtered_groups[x][max_p] = all_filtered
                self.counts = pd.concat([self.counts, pd.DataFrame([type_counter])])

        self.created_type_distributions = True
        return self.counts, self.filtered_groups
    
    def visualize_type_distributions(self, path:str=None) -> None:
        '''
        This function visualizes the counts of different types of multiple infection events (union, part_of_other_group, overlap) for each combination of range and maximum p-value.

        Args:
            path (str): The path to save the figure. If not set, the figure will be shown but not saved.
        '''

        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return
        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return

        ratio = len(self.xs)/len(self.max_p_vals)
        size = 15
        fig, axes = plt.subplots(nrows=len(self.xs), ncols=len(self.max_p_vals), figsize=(size,size*ratio))
        fig.supxlabel("<<<<     different maximum p-values      <<<<")
        fig.supylabel("<<<<     different range values     <<<<")
        fig.subplots_adjust(left=0.06, bottom=0.06, right=1, top=1)
        for i, x in enumerate(self.xs):
            for j, p in enumerate(sorted(self.max_p_vals)):
                row = self.counts[(self.counts['max_p']==p) & (self.counts['x']==x)].iloc[0]
                c1 = int(row['union'])
                c2 = int(row['part_of_other_group'])
                c3 = int(row['overlap'])
                ax = axes[i][j]
                ax.set_title(f"range: {x} | maximum p-value: {p}", fontdict={"fontsize": 9})
                ax.set_xticks([])
                ax.set_yticks([0.5, 1, 10, 100])
                ax.set_ylim(0.5, 100)
                ax.set_yscale("log")
                ax.bar([0,1,2], [c1,c2,c3], color=['blue', 'orange', 'red'])
                ax.text(0, 0.65, c1 if c1>0 else "", ha='center', va='center', fontdict={"fontsize": 11, 'c':'white'})
                ax.text(1, 0.65, c2 if c2>0 else "", ha='center', va='center', fontdict={"fontsize": 11, 'c':'white'})
                ax.text(2, 0.65, c3 if c3>0 else "", ha='center', va='center', fontdict={"fontsize": 11, 'c':'white'})
        if path: fig.savefig(path)
        fig.show()
    
    def visualize_noise_vs_data(self, path:str=None) -> None:
        '''
        This function visualizes the noise vs data ratio for different combinations of range and maximum p-value.
        The noise is calculated as 1 - (count of union groups / full count of all types).
        The data is calculated as the count of union groups.

        Args:
            path (str): The path to save the figure. If not set, the figure will be shown but not saved.
        '''

        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return
        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return

        scores = pd.DataFrame()
        for max_p in self.max_p_vals:
            for x in self.xs:
                row = self.counts[(self.counts['max_p']==max_p) & (self.counts['x']==x)].iloc[0]
                count = row['union']
                full = row['union']+row['part_of_other_group']+row['overlap']
                if full == 0:
                    ratio = 1
                else:
                    ratio = count/full
                curr = pd.DataFrame([{'max_p':max_p, 'x':x, 'count': count, 'ratio': 1-ratio}])
                scores = pd.concat([scores, curr])

        plt.figure(figsize=(13,8))
        sns.scatterplot(data=scores, x='count', y='ratio')
        plt.xlabel("data (count of first type)")
        plt.ylabel("noise (1 - ratio of first type)")
        plt.title("NOISE VS DATA")
        if path: plt.savefig(path)
        plt.show()
    
    def set_parameters(self, selected_range:float, selected_max_p_val:float) -> None:
        '''
        Sets the parameters for filtering the groups. The selected_x and selected_max_p_val should be one of the values from self.xs and self.max_p_vals respectively.
        
        Args:
            selected_x (float): The range value to select from self.xs.
            selected_max_p_val (float): The maximum p-value to select from self.max_p_vals.
        '''

        if selected_range not in self.xs:
            print("ERROR:\tselected_x should be one of the range values")
            return
        if selected_max_p_val not in self.max_p_vals:
            print("ERROR:\tselected_max_p_val should be one of the maximum p-values")
            return
        self.selected_x = selected_range
        self.selected_max_p_val = selected_max_p_val

        self.selected_parameters = True

    def get_filtered_groups(self, selected_x:float=None, selected_max_p_val:float=None) -> pd.DataFrame:
        '''
        Getter for the filtered groups dictionary with the selected parameters.

        Args:
            selected_x (float): The range value to select from self.xs. If not specified the function will use the previously set selected_x. If not set, it will return an error.
            selected_max_p_val (float): The maximum p-value to select from self.max_p_vals. If not specified the function will use the previously set selected_max_p_val. If not set, it will return an error.
    
        Returns:
            filtered_groups (pd.DataFrame): A DataFrame containing the filtered groups with the selected parameters.
        '''

        if not self.created_type_distributions:
            print("WARNING:\tYou need to run create_type_distributions() first to see the types of the groups")
            return
        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters and not (selected_x and selected_max_p_val):
            print("ERROR:\tYou need to set the parameters with set_parameters() first or specify them in the function")
            return
        if selected_x:
            if selected_x not in self.xs:
                print("ERROR:\tselected_x should be one of the range values")
                return
        else:
            selected_x = self.selected_x
        if selected_max_p_val:
            if selected_max_p_val not in self.max_p_vals:
                print("ERROR:\tselected_max_p_val should be one of the maximum p-values")
                return
        else:
            selected_max_p_val = self.selected_max_p_val
        
        return self.filtered_groups[selected_x][selected_max_p_val].copy()      

    def visualize_filtered_clusters(self, path:str=None, pdf_pages:PdfPages=None, show_sgids:bool=False, data_sgid_col:str="sgid") -> None:
        '''
        Visualizes the filtered clusters based on the selected parameters. It will visualize each cluster in a separate plot and save them to the specified path or show them if pdf_pages is None.

        Args:
            path (str): The path to save the figures. If not set, the figures will be shown but not saved.
            pdf_pages (PdfPages): If set, the figures will be saved to the PdfPages object instead of showing them. If not set, the figures will be shown but not saved.
            show_sgids (bool): If set, the sgids will be shown in the title of the plot. If not set, the sgids will not be shown.
            data_sgid_col (str): The name of the column in the DataFrame that contains the sgids. If show_sgids is set to True, this column will be used to show the sgids in the title of the plot.
        '''

        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters:
            print("ERROR:\tYou need to set the parameters with set_parameters() first")
            return
        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return

        filtered = self.filtered_groups[self.selected_x][self.selected_max_p_val]
        for i, (_, row) in enumerate(filtered.iterrows()):
            data = self.datasets[row['dataset_id']]
            ids = row['ids']
            cluster_path = f"{path.split('.')[0]}_{i}.{path.split('.')[-1]}" if path else None
            title = f"{row['dataset_id']}: {row['short_id']} ({row['type']}) -- {row[f'max_p_{self.selected_x}']:.3f} ({self.selected_x})"
            visualize_cluster(data, (min(ids), max(ids)), data_size_col=self.size_col, 
                              path=cluster_path, title=title, pdf_pages=pdf_pages, 
                              show=pdf_pages is None, close=pdf_pages is not None,
                              show_sgids=show_sgids, data_sgid_col=data_sgid_col)
    
    def get_interaction_counts(self, gene_col, n:int=2, calc_p_values:bool=False, iterations:int=1000, normalized_count:bool=True) -> pd.DataFrame:
        '''
        Calculates the interaction counts of genes in the filtered groups. It counts how many times each combination of n genes appears in the filtered groups.
        Args:
            gene_col (str): The name of the column in the DataFrame that contains the gene names.
            n (int): The number of genes to consider in the combinations. Default is 2 (gene pairs).
            calc_p_values (bool): If set to True, the function will calculate the p-values for the interaction counts by shuffling the genes in the datasets. Default is False.
            iterations (int): The number of iterations to run for the p-value calculations. Default is 1000.
            normalized_count (bool): If set to True, the counts will be normalized by the number of combinations of genes in each group.
        Returns:
            interactions (pd.DataFrame): A DataFrame containing the interaction counts of genes in the filtered groups. If calc_p_values is set to True, the DataFrame will also contain the p-values for the interaction counts.
        '''
        
        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters:
            print("ERROR:\tYou need to set the parameters with set_parameters() first")
            return
        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return
        
        groups = self.get_filtered_groups()
        groups['sgids'] = groups.apply(lambda row: list(set(self.datasets[row['dataset_id']].loc[row['ids'], gene_col].values)), axis=1)

        all_genes = set()
        for dataset in self.datasets.values():
            for g in set(dataset[gene_col].unique()):
                all_genes.add(g)
        
        combinations = list(map(lambda x: ";".join(sorted(x)), itertools.combinations(all_genes, n)))

        occurrences = {combination: 0 for combination in combinations}
        for _, row in groups.iterrows():
            data = self.datasets[row['dataset_id']]
            ids = row['ids']
            genes = list(set(data.loc[ids, gene_col]))
            num_genes = len(genes)
            divider = num_genes*(num_genes-1)/2 if normalized_count else 1
            current_combinations = list(map(lambda x: ";".join(sorted(x)), itertools.combinations(genes, n)))
            for curr_combination in current_combinations:
                occurrences[curr_combination] += 1/divider
        interactions = pd.DataFrame()
        interactions['combination'] = list(occurrences.keys())
        interactions['count'] = list(occurrences.values())

        if calc_p_values:

            occurences_pval = {combination: [] for combination in combinations}
            for i in range(iterations):
                echo(i, range(iterations))
                for combination in combinations:
                    occurences_pval[combination].append(0)
                
                for _, row in groups.iterrows():
                    data = self.datasets[row['dataset_id']]
                    ids = row['ids']
                    shuffled_genes = np.random.choice(data.head(self.max_index)[gene_col].values, size=self.max_index, replace=False)
                    genes = list(set(shuffled_genes[ids]))
                    num_genes = len(genes)
                    divider = num_genes*(num_genes-1)/2 if normalized_count else 1
                    current_combinations = list(map(lambda x: ";".join(sorted(x)), itertools.combinations(genes, n)))
                    for curr_combination in current_combinations:
                        occurences_pval[curr_combination][i] += 1/divider
            
            interactions_shuffled = pd.DataFrame()
            interactions_shuffled['combination'] = list(occurences_pval.keys())
            for i in range(iterations):
                interactions_shuffled[f'count_{i}'] = list(map(lambda x: occurences_pval[x][i], occurences_pval.keys()))
            interactions = pd.merge(interactions, interactions_shuffled, how='outer', on='combination')
            interactions['pval'] = interactions.apply(lambda row: len(list(filter(lambda value: row[1]<=value, row[2:])))/iterations, axis=1)


        interactions = interactions.sort_values("count", ascending=False)
        return interactions

    def visualize_neighbouring_ratios(self, path:str=None) -> None:
        '''
        Visualizes the ratios of neighbouring clone/tumor sizes in the filtered groups.

        Args:
            path (str): The path to save the figure. If not set, the figure will be shown but not saved.
        '''

        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters:
            print("ERROR:\tYou need to set the parameters with set_parameters() first")
            return
        
        filtered = self.get_filtered_groups()
        ratios = []
        for _, row in filtered.iterrows():
            data = self.datasets[row['dataset_id']]
            sizes = data[self.size_col].values
            ids = row['ids']
            curr_sizes = list(sizes[min(ids):max(ids)+1])

            for i in range(len(curr_sizes)-1):
                ratios.append(curr_sizes[i]/curr_sizes[i+1])
        plt.figure(figsize=(13,8))
        sns.histplot(ratios, kde=True)
        plt.ylabel("count")
        plt.xlabel("neighbouring ratios")
        if path: plt.savefig(path)
        plt.show()

    def get_probability_of_coinfection(self) -> tuple[float, int, int]:
        '''
        Calculates the probability of coinfection based on the filtered groups.
        Returns:
            ratio (float): The probability of coinfection.
            coinfecting_count (int): The count of coinfecting clusters (clusters with multiple infections).
            clone_count (int): The total number of clones/tumors considered in the analysis.
        '''

        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters:
            print("ERROR:\tYou need to set the parameters with set_parameters() first")
            return
        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return
        
        clone_count = len(self.datasets) * self.max_index
        groups = self.get_filtered_groups()
        groups = groups[groups['type']=='union'].copy()
        groups['cluster_size'] = groups['ids'].apply(len)
        coinfecting_count = groups['cluster_size'].sum()
        
        return coinfecting_count/clone_count, coinfecting_count, clone_count

    def get_coinfecting_cluster_size_distribution(self) -> list[int]:
        '''
        Returns the distribution of coinfecting cluster sizes (the number of clones/tumors in each multiple infection event).
        This is only for 'union' clusters, as they are the ones that are considered coinfecting.
        Returns:
            cluster_sizes (list[int]): A list of integers representing the sizes of the coinfecting clusters.
        '''

        if not self.ran_p_val:
            print("ERROR:\tYou need to run run_p_value_functions() first (and then create_type_distributions())")
            return
        if not self.selected_parameters:
            print("ERROR:\tYou need to set the parameters with set_parameters() first")
            return
        if not self.created_type_distributions:
            print("ERROR:\tYou need to run create_type_distributions() first")
            return
        
        f = self.get_filtered_groups()
        all_clusters = f.shape[0]
        f = f[f['type']=='union']
        union_clusters = f.shape[0]
        d = all_clusters - union_clusters
        if d > 0:
            print(f"WARNING:\tCalculating probability only for 'union' clusters. Throwing out {d} cluster(s).")
        f['cluster_size'] = f['ids'].apply(len)

        return list(f['cluster_size'].values)

    def full_pipeline(self) -> None:
        '''
        Runs the full pipeline of the coinfection detecting algorithm.
        '''

        self.run_p_value_functions()
        _ = self.create_type_distributions()
        self.visualize_type_distributions()
        self.visualize_noise_vs_data()
        input_x = float(input("Selected x: "))
        input_max_p_val = float(input("Selected max_p_val: "))
        self.set_parameters(input_x, input_max_p_val)
        self.visualize_filtered_clusters()
        self.visualize_neighbouring_ratios()
