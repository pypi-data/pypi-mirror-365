from libflowcam import ROIReader

# Represents a typical sample density
sample1 = ROIReader("testdata/flowcam_polina_pontoon_0907_r2/flowcam_polina_pontoon_0907_r2.csv")
print(str(len(sample1.rois)) + " ROIs") # Should be 6268 ROIs
for roi_index in [10, 100, 1000]:
    sample1.rois[roi_index].image.save("testout/flowcam_polina_pontoon_0907_r2_" + str(roi_index) + ".png")

# A very dense sample, this is a cruel test
sample2 = ROIReader("testdata/flowcam_polina_pontoon_0707_r1/flowcam_polina_pontoon_0707_r1.csv")
print(str(len(sample2.rois)) + " ROIs") # Should be 137015 ROIs
for roi_index in [0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000]:
    sample2.rois[roi_index].image.save("testout/flowcam_polina_pontoon_0707_r1_" + str(roi_index) + ".png")

# + list(range(100000,101000))
