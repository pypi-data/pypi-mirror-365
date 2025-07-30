import os
import math
import numpy as np
import cv2

from .helpers import get_display_aspect_ratio


def showProgressBar(i, arrlen, barlen=50):
    bar = "#" * int((i+1) / arrlen * barlen) + "-" * int((arrlen-i-1) / arrlen * barlen)
    print("\r", "{} ({} / {})     ".format(bar, i+1, arrlen), flush=True, end='')


def extract_stills_from_video(video_path: str, destination: str, fn_root='still', jump_frames=300, start_perc=0, end_perc=100, top_stillness=40, quiet=False):
    if not quiet: print("Using jump of {} frames:".format(jump_frames))

    stream = cv2.VideoCapture(video_path)
    
    # Determine if display aspect ratio is different from raw aspect ratio
    raw_w = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
    raw_h = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
    SAR = raw_w / raw_h
    DAR = get_display_aspect_ratio(video_path)
    incorrect_raw_aspect = (abs(DAR - SAR) > 0.01) if DAR else False
    
    # determine frame variables
    number_of_frames = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_start = int(number_of_frames * start_perc/100)
    frame_end = int(number_of_frames * end_perc/100)
    frame_n = frame_start

    stills = [] # item: (path, stillness_score, sharpness_score)
    while True:
        frame_n += jump_frames
        if not quiet: showProgressBar(frame_n-frame_start, frame_end-frame_start)
        if frame_n > frame_end:
            print('Reached end frame {} ({}%)'.format(frame_end, end_perc))
            break
        
        # get frame
        stream.set(1, frame_n)
        hasFrames, frame = stream.read()
        nextHasFrames, nextFrame = stream.read()
        if hasFrames == False or nextHasFrames == False:
            break
        stillness = np.mean((frame - nextFrame) ** 2)       # type: ignore
        sharpness = np.mean(cv2.Canny(frame, 50, 250)) * 10 # type: ignore
        if sharpness < 2:
            continue

        # save frame
        savepath = r"{}\{}_{}_{}_{}.jpg".format(destination, fn_root, (5-len(str(frame_n))) * "0" + str(frame_n), int(round(stillness,0)), int(round(sharpness,0)))
        if incorrect_raw_aspect and DAR:
            new_w = int(DAR * raw_h)
            frame = cv2.resize(frame, (new_w, raw_h))
        cv2.imwrite(savepath, frame)
        stills.append( (savepath, stillness, sharpness) )
    
    # filter stills
    stills.sort(key=lambda item: item[1]) # sort by stillness
    stills = stills[:int(len(stills)*top_stillness/100)]
    stills.sort(key=lambda item: item[2]) # sort by sharpness
    stills = stills[:int(len(stills)*85/100)]
    
    # remove temppaths
    videopaths = [ path for path, _, _ in stills ]
    for temp in os.listdir(destination):
        temppath = r"{}\{}".format(destination, temp)
        if temppath not in videopaths:
            os.remove(temppath)
    
    return stills

# flooding functions
def getHistogram(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.histogram(gray, bins=50, range=(0, 255))[0]

def getHistogramRMSDiff(hist1, hist2):
    return float(np.mean( ( hist1 - hist2 ) ** 2 ) / 1000000)


def floodingMethod(image_items: list[dict], stills_amount:int=10) -> list[dict]:
    if len(image_items) <= stills_amount:
        return image_items
    # print('FLOODING METHOD:')
    # print('amount of items:', len(image_items))
    selected_items, buffered_items = [], []
    queue = [ (item, getHistogram(item['image'])) for item in image_items ]
    queue.sort(reverse=True, key = lambda item: item[0]['score'])
    difference_thresh = 500.0
    min_score = 0.2
    while len(selected_items) < stills_amount:
        top_tuple = queue.pop(0)
        hist = top_tuple[1]
        min_diff = min((getHistogramRMSDiff(hist, hist_cmp) for _, hist_cmp in selected_items), default=float('inf'))
        if min_diff >= difference_thresh and top_tuple[0]['score'] >= min_score:
            selected_items.append(top_tuple)
            # print('{:>2} ADDED   ({:>3})  {:.1f}  score={:.1f}'.format(len(selected_items), difference_thresh, min_diff, top_tuple[0]['score']))
        else:
            buffered_items.append(top_tuple)
            # print('skipping    ({:>3})  {:>}'.format(difference_thresh, min_diff))
        if queue == []:
            queue = buffered_items.copy()
            buffered_items = []
            difference_thresh *= 0.5
            min_score *= 0.5
            # print('lowered diff thresh:', difference_thresh)
    image_items = [ item for item, _ in selected_items ]
    image_items.sort(reverse=True, key=lambda item: item['score'])
    # print()
    return image_items


#### HELPERS ####

class Colors:
    colors = [(255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 0 ,0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (0, 0, 0)]
    i = 0
    red = (0, 0, 255)
    cyan = (255, 255, 0)
    green = (0, 255, 0)

    @classmethod
    def next(cls):
        cls.i += 1
        if cls.i >= len(cls.colors):
            cls.i = 0
        return cls.colors[cls.i]

def addDetectionsToImage(image, detections):
    for j, det in enumerate(detections):
        detclass = det['class']
        score = det['score']
        (x, y, wid, hei) = det['box']
        color = Colors.next()
        cv2.rectangle(image, (x, y), (x+wid, y+hei), color, 2)
        cv2.putText(image, detclass, (x+10,y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)
        cv2.putText(image, str(round(score,2)), (x+10,y+43), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)

def get_detections_score(detections, imshape):
        if len(detections) == 0:
            return 0
        SCORE_THRESH = 0.25
        class_scores = {"FACE_FEMALE" : 12.75, "FACE_MALE": 0.4, "BUTTOCKS_EXPOSED": 2, 'BUTTOCKS_COVERED': 2, "FEMALE_BREAST_EXPOSED": 1.5,
        "FEMALE_BREAST_COVERED": 1.5, "ARMPITS_EXPOSED": 1, "FEET_EXPOSED": 1, "BELLY_EXPOSED": 0.75,
        "MALE_GENETALIA_EXPOSED": 0.5}
        (res_y, res_x, c) = imshape
        half_hei, half_wid = res_y/2, res_x/2
        diag_sq = (half_hei)**2 + (half_wid)**2
        area, spread, noncentered, recognition, number_bonus, class_score = 0, 0, 0, 0, 0, 0
        verteces = []
        bonus = 1
        maleFaceAdded = False
        for det in detections:
            detclass = det['class']
            if detclass == "FACE_MALE":
                if not maleFaceAdded:
                    class_score += class_scores.get(detclass, 0)
                maleFaceAdded = True
            else:
                class_score += class_scores.get(detclass, 0)
            score = det['score']
            (x, y, wid, hei) = det['box']
            verteces = verteces + [(x, y), (x+wid, y+hei)]
            if score > SCORE_THRESH:
                recognition += (score - SCORE_THRESH) * bonus
            number_bonus += bonus
            bonus /= 1.5
        verteces.sort(key = lambda item: item[0])
        x_min, x_max = verteces[0][0], verteces[-1][0]
        verteces.sort(key = lambda item: item[1])
        y_min, y_max = verteces[0][1], verteces[-1][1]
        box = (x_max - x_min, y_max - y_min)
        mid = (x_min + box[0]/2, y_min + box[0]/2)
        disp_sq = (half_wid-mid[0])**2 + (half_hei-mid[1])**2
        spread_score = math.pow((box[0] * box[1]), 0.5)
        max_spread_score = math.pow(res_x*res_y, 0.5)
        noncentered = disp_sq / diag_sq
        spread_score = spread_score / max_spread_score
        area =          area            * 0
        spread_score =  spread_score    * 1
        noncentered =   noncentered     * -2
        recognition =   recognition     * 1
        number_bonus =  number_bonus    * 0.2
        class_score =   class_score     * 0.1
        metrics = (area, spread_score, noncentered, recognition, number_bonus, class_score)
        score = sum(metrics)
        return score
