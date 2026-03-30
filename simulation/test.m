clear;
clc;
close all; 
target_pos_h = [10; 0; 0; 1]; 

Translation_Matrix = trvec2tform([5, 2, 0]); 

final_pos_h = Translation_Matrix * target_pos_h;

figure;
hold on;

plotTransforms([0 0 0], [1 0 0 0], 'FrameColor', 'red', 'FrameLabel', 'Base');

plotTransforms(target_pos_h(1:3)', [1 0 0 0], 'FrameColor', 'blue', 'FrameLabel', 'Target');

plotTransforms(final_pos_h(1:3)', [1 0 0 0], 'FrameColor', 'green', 'FrameLabel', 'Transformed');

grid on;
axis equal;
view(3);
xlabel('X'); ylabel('Y'); zlabel('Z');
title('Robot Frame Transformation');