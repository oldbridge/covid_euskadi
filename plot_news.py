# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 15:36:48 2021

@author: Xabi
"""

from functions import read_from_csv_net, read_populations
import matplotlib.pyplot as plt


if __name__ == '__main__':
    df = read_from_csv_net()
    
    fig, ax = plt.subplots(5, 1, sharex=True)
    
    sizes = read_populations()
    show_city = 'Usurbil'
    
    data = df['global']
    ax[0].plot(data['total_tests'])
    ax[0].plot(data['pcr_positives'])
    ax0_twin = ax[0].twinx()  # instantiate a second axes that shares the same x-axis
    ax0_twin.plot(data['positivity_rate'] * 100, 'r')
    ax[0].grid(True)
    ax[0].legend(['Total tests', 'Positive tests'])
    ax0_twin.set_ylabel('Positivity rate (%)')
    ax[0].set_ylabel("Number of tests")
    
    ax[1].plot(data['total_deaths'])
    ax1_twin = ax[1].twinx()
    ax1_twin.plot(data['daily_deaths'], 'r')
    ax1_twin.set_ylabel('Daily deaths')
    ax[1].set_ylabel("Total deaths")
    ax[1].legend(["Total deaths"])
    ax[1].grid(True)
    
    ax[2].plot(data['uci_total'])
    ax[2].plot(data.index, [500] * len(data.index), 'r--')
    ax[2].legend(['ICU occupation', 'Available ICU'])
    ax[2].set_ylabel("ICU beds")
    ax[2].grid(True)
    
    ax[3].plot(data['new_intake'])
    ax[3].plot(data['hosp_release_daily'])
    ax[3].legend(['New intake', 'Releases'])
    ax[3].set_ylabel("Patients")
    ax[3].grid(True)
    
    city_data = df['municipios'][show_city]
    city_size = sizes[sizes.index == show_city]['inhabitants'][0]
    ax[4].plot(city_data)
    inci_abs = city_data.rolling(14).sum()
    inci_100k = inci_abs * 100000 / city_size
    ax4_twin = ax[4].twinx()
    ax4_twin.plot(inci_100k, 'r')
    ax4_twin.set_ylabel('14 day incidence per 100k inhabitants')
    ax[4].legend(['Daily positives'])
    ax[4].set_ylabel("Patients")
    ax[4].grid(True)