import streamlit as st
from matplotlib import pyplot as plt
import numpy as np
import cv2
import pydicom
import zipfile
import io

def main():
    st.title('Machiron')
    file = st.file_uploader('Escolha um arquivo...', type=['zip','png','jpg','jpeg','gif'])
    if file is not None:
        #st.text(file.getvalue())
        #show_image(file) 
        extract_zip(file)

def show_image(image):
    bgr = cv2.split(image)
    hsv_image = cv2.calcHist(bgr, [0], None, [256], (0,256),accumulate=False)
    st.line_chart(hsv_image)

def extract_zip(file):
    with zipfile.ZipFile(file) as thezip:
        for zipinfo in thezip.infolist():
            with thezip.open(zipinfo) as thefile:
                dicom_file(zipinfo.filename, thefile)

def dicom_file(filename, file):
    dataset = pydicom.dcmread(file)
    show_dcm_info(filename, dataset)
    plot_pixel_array(dataset)
    show_image(dataset.pixel_array)

def plot_pixel_array(dataset):
    st.image(dataset.pixel_array, width=300)

def show_dcm_info(filename,  dataset):
    st.write("Filename.........:", filename)
    st.write("Storage type.....:", dataset.SOPClassUID)

    pat_name = dataset.PatientName
    display_name = pat_name.family_name + ", " + pat_name.given_name
    st.write("Patient's name......:", display_name)
    st.write("Patient id..........:", dataset.PatientID)
    st.write("Patient's Age.......:", dataset.PatientAge)
    st.write("Patient's Sex.......:", dataset.PatientSex)
    st.write("Modality............:", dataset.Modality)
    st.write("Body Part Examined..:", dataset.BodyPartExamined)
    st.write("View Position.......:", dataset.ViewPosition)
    
    if 'PixelData' in dataset:
        rows = int(dataset.Rows)
        cols = int(dataset.Columns)
        st.write("Image size.......: {rows:d} x {cols:d}, {size:d} bytes".format(
            rows=rows, cols=cols, size=len(dataset.PixelData)))
        if 'PixelSpacing' in dataset:
            st.write("Pixel spacing....:", dataset.PixelSpacing)

if __name__ == '__main__':
	main()

