import os
import streamlit as st
import pandas as pd
from Sort import sort
from process_video import process_video
import time
from interpolate_data import interpolate_results
from visualize import visualize_results
f

st.set_page_config(layout='wide')

st.title('Vehicle Detection and License Plate Recognition')


with st.sidebar:
    st.title('Plate Vision AI')
    st.image('assets/logo.png', use_column_width=True) 
    st.info('⚠️ Due to very low processing power, the video processing may take a while. That is why it has not been able to process the video real-time. The video will be processed in the background and the results will be displayed here once the processing is complete.')
    st.info('Models were trained to identify following formats of license plates: \n')
    st.image('assets/license_plate1.png', use_column_width=True)
    st.image('assets/license_plate2.png', caption='First two characters are letters, next two are digits, and last three are letters.', use_column_width=True)
    
col1, col2 = st.columns(2)
with col1:
    videos = os.listdir(os.path.join('..', 'sample_videos'))
    st.subheader('Select a sample video')
    selected_video = st.selectbox('',videos)
    
with col1:
    st.subheader('Or upload your own video')
    uploaded_file = st.file_uploader('Drag and drop a video file here', type=['mp4']) 
    
    
    
# Initialize session state variables
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'interpolated' not in st.session_state:
    st.session_state.interpolated = False
if 'visualized' not in st.session_state:
    st.session_state.visualized = False

if selected_video or uploaded_file:
    
    if uploaded_file:
        selected_video = uploaded_file.name
        with open(os.path.join('..', 'uploaded_videos', selected_video), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        file_path = os.path.join('..', 'sample_videos', selected_video)
        
        
    else:
        file_path = os.path.join('..', 'sample_videos', selected_video)
    
    with col1:
        st.info('Preview of the video')
        video_file = open(file_path, 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        # Create a button to process the video
        if st.button('Process Video'):
            st.toast('Processing video... This may take a while...')
            process_video(file_path)
            st.session_state.processed = True
            
        # Read and display the results CSV
        results_path = './results.csv'
        if os.path.exists(results_path):
            st.session_state.processed = True
            results_df = pd.read_csv(results_path)
            
            with col2:
                st.toast('Video processed successfully!')
                st.info('Detected vehicles and license plates in each frame')
                st.dataframe(results_df)
            
            button1, button2, button3 = st.columns(3)

            with button1:
                if st.button('Interpolate Results'):
                    st.toast('Interpolating results...')
                    interpolate_results(results_path, 'results_interpolated.csv')
                    st.session_state.interpolated = True
                    
            with button2:
                interpolated_results_path = './results_interpolated.csv'
                if os.path.exists(interpolated_results_path):
                    st.session_state.interpolated = True
                    if st.button('Visualize Output'):
                        st.toast('Processing video... This may take a while...')
                        visualize_results(file_path, interpolated_results_path, 'output.mp4')
                        st.session_state.visualized = True
                        
            with col2:
                if st.session_state.interpolated:
                    id = pd.read_csv('results_interpolated.csv')
                    st.info('Results after interpolation')
                    st.dataframe(id)
                    
            with col1:
                if os.path.exists('output.mp4'):
                    st.session_state.visualized = True
                    st.info('Preview of the processed video')
                    video_file_ = open('output_reencoded.mp4', 'rb')
                    video_bytes_ = video_file_.read()
                    st.video(video_bytes_)
                            
        else:
            st.error('No results found. Please process the video first.')
