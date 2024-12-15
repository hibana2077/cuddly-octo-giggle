import pandas as pd

if __name__ == '__main__':
    master_dir = './walk/normal/'

    # Load the data
    smoothness_data = pd.read_csv(f'{master_dir}smoothness_values.csv')
    # smoothness_data drop first row
    smoothness_data = smoothness_data.drop(0)
    dcr_data = pd.read_csv(f'{master_dir}dcr_values.csv')
    jad_data = pd.read_csv(f'{master_dir}jad_values.csv')

    aggregated_data = pd.merge(smoothness_data, dcr_data, on='Frame')
    aggregated_data = pd.merge(aggregated_data, jad_data, on='Frame')

    # Save the aggregated data
    aggregated_data.to_csv(f"{master_dir}aggregated_data.csv", index=False)