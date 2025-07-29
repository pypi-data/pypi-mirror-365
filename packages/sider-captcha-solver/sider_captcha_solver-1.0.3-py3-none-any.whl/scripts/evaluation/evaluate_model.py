"""
综合模型评估工具
功能：
1. 评估最优模型在两个数据集上的表现
2. 分析训练过程中准确率的变化趋势
3. 生成可视化结果和详细报告

运行模式：
- python evaluate_model.py --mode best：评估最优模型
- python evaluate_model.py --mode training：分析训练准确率变化
- python evaluate_model.py --mode all：执行所有评估
"""
import sys
from pathlib import Path
import numpy as np
import random
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
from datetime import datetime
import pandas as pd
import logging
import argparse
import re
import toml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.predictor import CaptchaPredictor


def get_version_from_pyproject():
    """从pyproject.toml读取版本号"""
    pyproject_path = project_root / 'pyproject.toml'
    if pyproject_path.exists():
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
                return data.get('project', {}).get('version', '1.0.0')
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")
            # 如果toml解析失败，尝试用正则表达式
            try:
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
                    if match:
                        return match.group(1)
            except Exception:
                pass
    return "1.0.0"


def calculate_mae(pred_center, gt_center):
    """计算平均绝对误差（仅x轴）"""
    if pred_center is None or gt_center is None:
        return float('inf')
    # 只计算x轴误差
    return np.abs(pred_center[0] - gt_center[0])


def evaluate_dataset(predictor, dataset_name, data_dir, annotations_path, 
                    output_dir, max_samples=1000, visualize_count=100):
    """评估单个数据集"""
    print(f"\n{'='*60}")
    print(f"Evaluating {dataset_name}")
    print(f"{'='*60}")
    
    # 准备样本
    samples = []
    
    # 如果annotations_path存在，从文件加载
    if annotations_path and annotations_path.exists():
        # 加载标注数据
        with open(annotations_path, 'r', encoding='utf-8') as f:
            annotations = json.load(f)
        
        for ann in annotations:
            img_path = data_dir / ann['filename']
            if img_path.exists():
                samples.append({
                    'path': str(img_path),
                    'filename': ann['filename'],
                    'bg_center': ann['bg_center'],
                    'slider_center': ann['sd_center']
                })
    else:
        # 从文件名解析坐标
        import re
        for img_path in data_dir.glob("*.png"):
            filename = img_path.name
            # 解析文件名格式：Pic0001_Bgx120Bgy70_Sdx30Sdy70_{hash}.png
            match = re.search(r'Pic(\d+)_Bgx(\d+)Bgy(\d+)_Sdx(\d+)Sdy(\d+)', filename)
            if match:
                bg_x = int(match.group(2))
                bg_y = int(match.group(3))
                sd_x = int(match.group(4))
                sd_y = int(match.group(5))
                
                samples.append({
                    'path': str(img_path),
                    'filename': filename,
                    'bg_center': [bg_x, bg_y],
                    'slider_center': [sd_x, sd_y]
                })
    
    print(f"Found {len(samples)} samples in {dataset_name}")
    
    # 限制样本数量
    if max_samples is not None and len(samples) > max_samples:
        samples = random.sample(samples, max_samples)
        print(f"Randomly selected {max_samples} samples for evaluation")
    
    # 随机选择可视化样本
    visualize_indices = random.sample(range(len(samples)), 
                                    min(visualize_count, len(samples)))
    
    # 创建输出目录
    vis_dir = output_dir / 'visualizations'
    vis_dir.mkdir(parents=True, exist_ok=True)
    
    # 评估指标
    gap_mae_list = []
    slider_mae_list = []
    gap_success_5px = 0
    slider_success_5px = 0
    gap_success_7px = 0
    slider_success_7px = 0
    both_success_5px = 0
    both_success_7px = 0
    gap_detected = 0
    slider_detected = 0
    
    print(f"\nProcessing {len(samples)} samples...")
    
    for i, sample in enumerate(tqdm(samples)):
        # 预测
        result = predictor.predict(sample['path'])
        
        # 获取真实标签
        gt_gap = np.array(sample['bg_center'], dtype=np.float32)
        gt_slider = np.array(sample['slider_center'], dtype=np.float32)
        
        # 提取预测结果
        pred_gap = None
        pred_slider = None
        
        if result['gap_x'] is not None:
            pred_gap = np.array([result['gap_x'], result['gap_y']])
            gap_detected += 1
            
        if result['slider_x'] is not None:
            pred_slider = np.array([result['slider_x'], result['slider_y']])
            slider_detected += 1
        
        # 计算MAE
        gap_mae = calculate_mae(pred_gap, gt_gap)
        slider_mae = calculate_mae(pred_slider, gt_slider)
        
        if gap_mae != float('inf'):
            gap_mae_list.append(gap_mae)
            if gap_mae <= 5:
                gap_success_5px += 1
            if gap_mae <= 7:
                gap_success_7px += 1
                
        if slider_mae != float('inf'):
            slider_mae_list.append(slider_mae)
            if slider_mae <= 5:
                slider_success_5px += 1
            if slider_mae <= 7:
                slider_success_7px += 1
        
        # 基于滑动距离判断成功率
        if pred_gap is not None and pred_slider is not None:
            gt_distance = gt_gap[0] - gt_slider[0]
            pred_distance = pred_gap[0] - pred_slider[0]
            distance_error = np.abs(pred_distance - gt_distance)
            
            if distance_error <= 5:
                both_success_5px += 1
            if distance_error <= 7:
                both_success_7px += 1
        
        # 可视化
        if i in visualize_indices:
            visualize_prediction(
                sample['path'], 
                pred_gap, pred_slider,
                gt_gap, gt_slider,
                result['gap_confidence'], result['slider_confidence'],
                vis_dir / f"sample_{i:04d}.png"
            )
    
    # 计算统计数据
    total = len(samples)
    results = {
        'dataset_name': dataset_name,
        'total_samples': total,
        'gap_detection_rate': gap_detected / total * 100,
        'slider_detection_rate': slider_detected / total * 100,
        'gap_mean_mae': np.mean(gap_mae_list) if gap_mae_list else float('inf'),
        'gap_std_mae': np.std(gap_mae_list) if gap_mae_list else 0,
        'gap_median_mae': np.median(gap_mae_list) if gap_mae_list else float('inf'),
        'gap_success_rate_5px': gap_success_5px / total * 100,
        'gap_success_rate_7px': gap_success_7px / total * 100,
        'slider_mean_mae': np.mean(slider_mae_list) if slider_mae_list else float('inf'),
        'slider_std_mae': np.std(slider_mae_list) if slider_mae_list else 0,
        'slider_median_mae': np.median(slider_mae_list) if slider_mae_list else float('inf'),
        'slider_success_rate_5px': slider_success_5px / total * 100,
        'slider_success_rate_7px': slider_success_7px / total * 100,
        'both_success_rate_5px': both_success_5px / total * 100,
        'both_success_rate_7px': both_success_7px / total * 100,
        'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 保存结果
    results_path = output_dir / 'evaluation_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 打印结果
    print_results(results)
    
    return results


def visualize_prediction(img_path, pred_gap, pred_slider, gt_gap, gt_slider, 
                        gap_conf, slider_conf, save_path):
    """可视化单个预测结果"""
    # 读取图片
    img = cv2.imread(str(img_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 创建图形
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.imshow(img)
    
    # 绘制真实位置（绿色实线）
    if gt_gap is not None:
        circle = patches.Circle((gt_gap[0], gt_gap[1]), 5, 
                              linewidth=2, edgecolor='green', facecolor='none')
        ax.add_patch(circle)
        ax.text(gt_gap[0], gt_gap[1] - 10, 'GT Gap', 
               color='green', fontsize=8, ha='center', weight='bold')
    
    if gt_slider is not None:
        circle = patches.Circle((gt_slider[0], gt_slider[1]), 5,
                              linewidth=2, edgecolor='green', facecolor='none')
        ax.add_patch(circle)
        ax.text(gt_slider[0], gt_slider[1] + 15, 'GT Slider',
               color='green', fontsize=8, ha='center', weight='bold')
    
    # 绘制预测位置（红色/蓝色虚线）
    if pred_gap is not None:
        circle = patches.Circle((pred_gap[0], pred_gap[1]), 5, 
                              linewidth=2, edgecolor='red', facecolor='none', linestyle='--')
        ax.add_patch(circle)
        mae_x = np.abs(pred_gap[0] - gt_gap[0])
        ax.text(pred_gap[0], pred_gap[1] - 20, 
               f'Pred Gap\nX-MAE:{mae_x:.1f}px\nConf:{gap_conf:.3f}', 
               color='red', fontsize=7, ha='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    if pred_slider is not None:
        circle = patches.Circle((pred_slider[0], pred_slider[1]), 5,
                              linewidth=2, edgecolor='blue', facecolor='none', linestyle='--')
        ax.add_patch(circle)
        mae_x = np.abs(pred_slider[0] - gt_slider[0])
        ax.text(pred_slider[0], pred_slider[1] + 25,
               f'Pred Slider\nX-MAE:{mae_x:.1f}px\nConf:{slider_conf:.3f}',
               color='blue', fontsize=7, ha='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # 显示滑动距离
    if pred_gap is not None and pred_slider is not None:
        distance = pred_gap[0] - pred_slider[0]
        ax.plot([pred_slider[0], pred_gap[0]], 
               [pred_slider[1], pred_gap[1]], 
               'purple', linewidth=1, alpha=0.5, linestyle=':')
        ax.text((pred_slider[0] + pred_gap[0]) / 2,
               (pred_slider[1] + pred_gap[1]) / 2 - 5,
               f"Distance: {distance:.1f}px",
               color='purple', fontsize=8, ha='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    ax.set_title(f'{Path(img_path).name}', fontsize=10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches='tight')
    plt.close()


def print_results(results):
    """打印评估结果"""
    print(f"\n{'-'*50}")
    print(f"Results for {results['dataset_name']}")
    print(f"{'-'*50}")
    print(f"Total samples: {results['total_samples']}")
    print(f"\nDetection rates:")
    print(f"  Gap: {results['gap_detection_rate']:.1f}%")
    print(f"  Slider: {results['slider_detection_rate']:.1f}%")
    print(f"\nMean Absolute Error (MAE, X-axis only):")
    print(f"  Gap: {results['gap_mean_mae']:.2f} ± {results['gap_std_mae']:.2f} px (median: {results['gap_median_mae']:.2f})")
    print(f"  Slider: {results['slider_mean_mae']:.2f} ± {results['slider_std_mae']:.2f} px (median: {results['slider_median_mae']:.2f})")
    print(f"\nSuccess rates (<=5 px):")
    print(f"  Gap: {results['gap_success_rate_5px']:.1f}%")
    print(f"  Slider: {results['slider_success_rate_5px']:.1f}%")
    print(f"  Distance-based: {results['both_success_rate_5px']:.1f}%")
    print(f"\nSuccess rates (<=7 px):")
    print(f"  Gap: {results['gap_success_rate_7px']:.1f}%")
    print(f"  Slider: {results['slider_success_rate_7px']:.1f}%")
    print(f"  Distance-based: {results['both_success_rate_7px']:.1f}%")


def create_summary_report(results_list, output_path, model_name='best_model.pth'):
    """创建汇总报告"""
    report = {
        'model': model_name,
        'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'datasets': results_list,
        'summary': {
            'average_gap_mae': np.mean([r['gap_mean_mae'] for r in results_list if r['gap_mean_mae'] != float('inf')]),
            'average_slider_mae': np.mean([r['slider_mean_mae'] for r in results_list if r['slider_mean_mae'] != float('inf')]),
            'average_both_success_5px': np.mean([r['both_success_rate_5px'] for r in results_list]),
            'average_both_success_7px': np.mean([r['both_success_rate_7px'] for r in results_list])
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report


def evaluate_best_model(model_paths=None):
    # 设置随机种子
    random.seed(42)
    np.random.seed(42)
    
    # 获取当前版本号
    current_version = get_version_from_pyproject()
    
    # 如果没有指定模型路径，使用默认路径
    if model_paths is None:
        # 首先尝试使用当前版本的模型
        checkpoints_dir = project_root / "src" / "checkpoints"
        current_version_model = checkpoints_dir / current_version / "best_model.pth"
        
        if current_version_model.exists():
            model_paths = [current_version_model]
            print(f"Using current version model: {model_paths[0]}")
        else:
            # 如果当前版本没有模型，查找所有版本的模型
            version_dirs = []
            
            # 查找所有版本目录
            if checkpoints_dir.exists():
                for dir_path in checkpoints_dir.iterdir():
                    if dir_path.is_dir():
                        # 检查是否是版本号格式
                        if re.match(r'^\d+\.\d+\.\d+$', dir_path.name):
                            best_model = dir_path / "best_model.pth"
                            if best_model.exists():
                                version_dirs.append(best_model)
            
            if version_dirs:
                # 按版本号排序
                version_dirs.sort(key=lambda x: x.parent.name, reverse=True)
                model_paths = [version_dirs[0]]  # 默认使用最新版本
                print(f"Using latest model: {model_paths[0]}")
            else:
                print("No best_model.pth file found in any version directory!")
                print(f"Please train a model first using: python scripts/training/train.py --version {current_version}")
                return
    elif isinstance(model_paths, (str, Path)):
        model_paths = [Path(model_paths)]
    
    # 存储所有模型的结果
    all_model_results = {}
    
    for model_path in model_paths:
        model_path = Path(model_path)
        model_name = model_path.stem
        
        print(f"\n{'='*80}")
        print(f"Evaluating model: {model_name}")
        print(f"Path: {model_path}")
        print(f"{'='*80}")
        
        predictor = CaptchaPredictor(
            model_path=str(model_path),
            device='auto',
            hm_threshold=0.1
        )
        
        results_list = []
        
        # 根据模型路径创建对应的结果目录
        # 例如: 1.0.3/best_model.pth -> checkpoints/1.0.3/evaluation/
        model_version = model_path.parent.name
        
        # 1. 评估测试数据集
        test_data_dir = project_root / "test_output" / "test"
        test_annotations_path = test_data_dir / "annotations.json"
        
        # 如果test_output/test不存在，尝试使用data/test
        if not test_data_dir.exists():
            test_data_dir = project_root / "data" / "test"
            test_annotations_path = test_data_dir / "annotations.json"
        
        test_results = evaluate_dataset(
            predictor,
            dataset_name="Test Dataset (Generated CAPTCHAs)",
            data_dir=test_data_dir,
            annotations_path=test_annotations_path if test_annotations_path.exists() else None,
            output_dir=project_root / "results" / model_version / "test_dataset",
            max_samples=1000,
            visualize_count=100  # 增加可视化样本数到100个
        )
        results_list.append(test_results)
        
        # 2. 评估真实验证码数据集
        real_data_dir = project_root / "data" / "real_captchas" / "annotated"
        real_annotations_path = real_data_dir / "annotations.json"
        
        if real_data_dir.exists():
            real_results = evaluate_dataset(
                predictor,
                dataset_name="Real CAPTCHAs",
                data_dir=real_data_dir,
                annotations_path=real_annotations_path if real_annotations_path.exists() else None,
                output_dir=project_root / "results" / model_version / "real_captchas",
                max_samples=100,
                visualize_count=50  # 可视化50个真实验证码样本
            )
            results_list.append(real_results)
        
        # 3. 创建汇总报告
        summary_report = create_summary_report(
            results_list,
            project_root / "results" / model_version / "summary_report.json",
            model_name=model_name
        )
        
        # 存储结果
        model_result = {
            'model_path': str(model_path),
            'test_results': test_results,
            'summary': summary_report['summary']
        }
        
        # 如果有真实验证码的结果，也存储
        if 'real_results' in locals():
            model_result['real_results'] = real_results
            
        all_model_results[model_name] = model_result
    
    # 比较所有模型
    if len(all_model_results) > 1:
        print(f"\n{'='*80}")
        print("MODEL COMPARISON")
        print(f"{'='*80}")
        
        comparison_data = []
        for model_name, results in all_model_results.items():
            comparison_data.append({
                'Model': model_name,
                'Gap MAE': f"{results['test_results']['gap_mean_mae']:.2f}",
                'Slider MAE': f"{results['test_results']['slider_mean_mae']:.2f}",
                'Success@5px': f"{results['test_results']['both_success_rate_5px']:.1f}%",
                'Success@7px': f"{results['test_results']['both_success_rate_7px']:.1f}%"
            })
        
        # 创建比较表格
        df = pd.DataFrame(comparison_data)
        print(df.to_string(index=False))
        
        # 保存比较结果到当前版本的results目录
        comparison_path = project_root / "results" / current_version / "model_comparison.csv"
        comparison_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(comparison_path, index=False)
        print(f"\nComparison saved to: {comparison_path}")
        
        # 找出最佳模型
        best_model = min(all_model_results.items(), 
                        key=lambda x: x[1]['test_results']['gap_mean_mae'] + x[1]['test_results']['slider_mean_mae'])
        print(f"\nBest model: {best_model[0]}")
        print(f"Combined MAE: {best_model[1]['test_results']['gap_mean_mae'] + best_model[1]['test_results']['slider_mean_mae']:.2f} px")


def setup_logging(log_dir):
    """设置日志记录"""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def calculate_accuracy_at_threshold(predictor, test_samples, threshold_px):
    """计算指定像素阈值下的准确率（基于滑动距离误差）"""
    distance_success = 0
    total = len(test_samples)
    
    for sample in test_samples:
        # 预测
        result = predictor.predict(sample['path'])
        
        # 获取真实标签
        gt_gap = np.array(sample['bg_center'], dtype=np.float32)
        gt_slider = np.array(sample['slider_center'], dtype=np.float32)
        
        # 计算真实的滑动距离（gap中心 - slider中心的x轴距离）
        gt_distance = gt_gap[0] - gt_slider[0]
        
        # 计算预测的滑动距离
        if result['gap_x'] is not None and result['slider_x'] is not None:
            pred_distance = result['gap_x'] - result['slider_x']
            
            # 计算滑动距离误差
            distance_error = np.abs(pred_distance - gt_distance)
            
            # 统计成功率
            if distance_error <= threshold_px:
                distance_success += 1
    
    return {
        'gap_accuracy': 0,  # 不再单独统计
        'slider_accuracy': 0,  # 不再单独统计
        'both_accuracy': distance_success / total * 100  # 基于滑动距离的准确率
    }


def analyze_training_progress():
    """分析训练过程中的准确率变化"""
    # 获取当前版本号
    current_version = get_version_from_pyproject()
    
    # 先确定使用哪个版本的checkpoints
    checkpoints_dir = project_root / "src" / "checkpoints"
    
    # 优先使用当前版本
    current_version_dir = checkpoints_dir / current_version
    if current_version_dir.exists() and any(current_version_dir.glob("checkpoint_epoch_*.pth")):
        log_dir = project_root / "results" / current_version / "training_analysis"
        log_dir.mkdir(parents=True, exist_ok=True)
        use_version = current_version
    else:
        # 否则查找最新版本
        version_dirs = []
        for dir_path in checkpoints_dir.iterdir():
            if dir_path.is_dir():
                if re.match(r'^\d+\.\d+\.\d+$', dir_path.name):
                    version_dirs.append(dir_path)
        
        if version_dirs:
            version_dirs.sort(key=lambda x: x.name, reverse=True)
            latest_version = version_dirs[0].name
            log_dir = project_root / "results" / latest_version / "training_analysis"
            log_dir.mkdir(parents=True, exist_ok=True)
            use_version = latest_version
        else:
            log_dir = project_root / "logs"
            use_version = None
    
    logger = setup_logging(log_dir)
    logger.info("="*60)
    logger.info("Starting training accuracy analysis")
    logger.info("="*60)
    
    # 加载测试数据
    test_data_dir = project_root / "data" / "test"
    annotations_path = test_data_dir / "annotations.json"
    test_samples = []
    
    if annotations_path.exists():
        with open(annotations_path, 'r', encoding='utf-8') as f:
            test_annotations = json.load(f)
        
        # 准备测试样本（使用前200个样本以加快评估速度）
        for ann in test_annotations[:200]:
            img_path = test_data_dir / ann['filename']
            if img_path.exists():
                test_samples.append({
                    'path': str(img_path),
                    'filename': ann['filename'],
                    'bg_center': ann['bg_center'],
                    'slider_center': ann['sd_center']
                })
    else:
        # 从文件名解析坐标
        import re
        for i, img_path in enumerate(test_data_dir.glob("*.png")):
            if i >= 200:  # 限制为200个样本
                break
            filename = img_path.name
            match = re.search(r'Pic(\d+)_Bgx(\d+)Bgy(\d+)_Sdx(\d+)Sdy(\d+)', filename)
            if match:
                bg_x = int(match.group(2))
                bg_y = int(match.group(3))
                sd_x = int(match.group(4))
                sd_y = int(match.group(5))
                
                test_samples.append({
                    'path': str(img_path),
                    'filename': filename,
                    'bg_center': [bg_x, bg_y],
                    'slider_center': [sd_x, sd_y]
                })
    
    logger.info(f"Using {len(test_samples)} test samples for evaluation")
    
    # 加载真实验证码数据
    real_data_dir = project_root / "data" / "real_captchas" / "annotated"
    real_annotations_path = real_data_dir / "annotations.json"
    real_samples = []
    
    if real_data_dir.exists() and real_annotations_path.exists():
        with open(real_annotations_path, 'r', encoding='utf-8') as f:
            real_annotations = json.load(f)
        
        # 准备真实验证码样本
        for ann in real_annotations:
            img_path = real_data_dir / ann['filename']
            if img_path.exists():
                real_samples.append({
                    'path': str(img_path),
                    'filename': ann['filename'],
                    'bg_center': ann['bg_center'],
                    'slider_center': ann['sd_center']
                })
    
    logger.info(f"Using {len(real_samples)} real CAPTCHA samples for evaluation")
    
    # 获取所有checkpoint文件 - 使用最新的版本目录
    checkpoints_dir = project_root / "src" / "checkpoints"
    checkpoint_files = []
    
    # 根据前面确定的版本查找checkpoint文件
    if use_version:
        version_dir = checkpoints_dir / use_version
        checkpoint_files = sorted(version_dir.glob("checkpoint_epoch_*.pth"))
        logger.info(f"Using checkpoints from: {version_dir}")
    else:
        checkpoint_files = []
        logger.warning("No version directory found with checkpoint files")
    
    results = {
        'epochs': [],
        # Test dataset results
        'test_5px_gap_accuracy': [],
        'test_5px_slider_accuracy': [],
        'test_5px_both_accuracy': [],
        'test_7px_gap_accuracy': [],
        'test_7px_slider_accuracy': [],
        'test_7px_both_accuracy': [],
        # Real dataset results
        'real_5px_gap_accuracy': [],
        'real_5px_slider_accuracy': [],
        'real_5px_both_accuracy': [],
        'real_7px_gap_accuracy': [],
        'real_7px_slider_accuracy': [],
        'real_7px_both_accuracy': []
    }
    
    logger.info(f"Found {len(checkpoint_files)} checkpoints to evaluate")
    
    for checkpoint_path in tqdm(checkpoint_files, desc="Evaluating epochs"):
        # 提取epoch号
        epoch_str = checkpoint_path.stem.split('_')[-1]
        epoch = int(epoch_str)
        
        logger.info(f"\nEvaluating epoch {epoch}...")
        
        try:
            # 加载模型
            predictor = CaptchaPredictor(
                model_path=str(checkpoint_path),
                device='auto',
                hm_threshold=0.1
            )
            
            # 计算测试集的5px和7px准确率
            test_metrics_5px = calculate_accuracy_at_threshold(predictor, test_samples, threshold_px=5)
            test_metrics_7px = calculate_accuracy_at_threshold(predictor, test_samples, threshold_px=7)
            
            # 计算真实数据集的5px和7px准确率
            real_metrics_5px = calculate_accuracy_at_threshold(predictor, real_samples, threshold_px=5)
            real_metrics_7px = calculate_accuracy_at_threshold(predictor, real_samples, threshold_px=7)
            
            # 记录结果
            results['epochs'].append(epoch)
            
            # Test dataset results
            results['test_5px_gap_accuracy'].append(test_metrics_5px['gap_accuracy'])
            results['test_5px_slider_accuracy'].append(test_metrics_5px['slider_accuracy'])
            results['test_5px_both_accuracy'].append(test_metrics_5px['both_accuracy'])
            results['test_7px_gap_accuracy'].append(test_metrics_7px['gap_accuracy'])
            results['test_7px_slider_accuracy'].append(test_metrics_7px['slider_accuracy'])
            results['test_7px_both_accuracy'].append(test_metrics_7px['both_accuracy'])
            
            # Real dataset results
            results['real_5px_gap_accuracy'].append(real_metrics_5px['gap_accuracy'])
            results['real_5px_slider_accuracy'].append(real_metrics_5px['slider_accuracy'])
            results['real_5px_both_accuracy'].append(real_metrics_5px['both_accuracy'])
            results['real_7px_gap_accuracy'].append(real_metrics_7px['gap_accuracy'])
            results['real_7px_slider_accuracy'].append(real_metrics_7px['slider_accuracy'])
            results['real_7px_both_accuracy'].append(real_metrics_7px['both_accuracy'])
            
            logger.info(f"Epoch {epoch} - Test 5px: Gap={test_metrics_5px['gap_accuracy']:.1f}%, "
                       f"Slider={test_metrics_5px['slider_accuracy']:.1f}%, Both={test_metrics_5px['both_accuracy']:.1f}%")
            logger.info(f"Epoch {epoch} - Test 7px: Gap={test_metrics_7px['gap_accuracy']:.1f}%, "
                       f"Slider={test_metrics_7px['slider_accuracy']:.1f}%, Both={test_metrics_7px['both_accuracy']:.1f}%")
            logger.info(f"Epoch {epoch} - Real 5px: Gap={real_metrics_5px['gap_accuracy']:.1f}%, "
                       f"Slider={real_metrics_5px['slider_accuracy']:.1f}%, Both={real_metrics_5px['both_accuracy']:.1f}%")
            logger.info(f"Epoch {epoch} - Real 7px: Gap={real_metrics_7px['gap_accuracy']:.1f}%, "
                       f"Slider={real_metrics_7px['slider_accuracy']:.1f}%, Both={real_metrics_7px['both_accuracy']:.1f}%")
            
        except Exception as e:
            logger.error(f"Error evaluating epoch {epoch}: {str(e)}")
            continue
    
    # 生成图表 - 保存到对应版本的checkpoints目录
    # log_dir 已经在函数开始设置好了，这里不需要重新设置
    
    
    # 生成对比图 - Both准确率对比
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 5px Both准确率对比
    ax1.plot(results['epochs'], results['test_5px_both_accuracy'], 'b-o', label='Test Dataset', markersize=8, linewidth=2)
    ax1.plot(results['epochs'], results['real_5px_both_accuracy'], 'r-s', label='Real CAPTCHAs', markersize=8, linewidth=2)
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Distance Accuracy (%)', fontsize=12)
    ax1.set_title('5-Pixel Threshold - Distance Accuracy Comparison', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 105)
    
    # 7px Both准确率对比
    ax2.plot(results['epochs'], results['test_7px_both_accuracy'], 'b-o', label='Test Dataset', markersize=8, linewidth=2)
    ax2.plot(results['epochs'], results['real_7px_both_accuracy'], 'r-s', label='Real CAPTCHAs', markersize=8, linewidth=2)
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Distance Accuracy (%)', fontsize=12)
    ax2.set_title('7-Pixel Threshold - Distance Accuracy Comparison', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 105)
    
    plt.suptitle('Test vs Real CAPTCHAs - Distance Accuracy Comparison', fontsize=16)
    plt.tight_layout()
    comparison_path = log_dir / 'accuracy_comparison.png'
    plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Comparison plot saved to: {comparison_path}")
    
    # 保存结果到CSV（格式化数值）
    csv_path = log_dir / 'training_accuracy_results.csv'
    df = pd.DataFrame(results)
    
    # 格式化所有准确率列为1位小数
    accuracy_columns = [col for col in df.columns if 'accuracy' in col]
    for col in accuracy_columns:
        df[col] = df[col].round(1)
    
    df.to_csv(csv_path, index=False, float_format='%.1f')
    logger.info(f"Results saved to CSV: {csv_path}")
    
    
    # 找出最佳epoch
    test_best_5px_epoch = results['epochs'][np.argmax(results['test_5px_both_accuracy'])]
    test_best_7px_epoch = results['epochs'][np.argmax(results['test_7px_both_accuracy'])]
    real_best_5px_epoch = results['epochs'][np.argmax(results['real_5px_both_accuracy'])]
    real_best_7px_epoch = results['epochs'][np.argmax(results['real_7px_both_accuracy'])]
    
    
    logger.info("\n" + "="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    logger.info("Test Dataset:")
    logger.info(f"  Best epoch for 5px threshold: Epoch {test_best_5px_epoch} "
               f"(Both accuracy: {max(results['test_5px_both_accuracy']):.1f}%)")
    logger.info(f"  Best epoch for 7px threshold: Epoch {test_best_7px_epoch} "
               f"(Both accuracy: {max(results['test_7px_both_accuracy']):.1f}%)")
    logger.info("\nReal CAPTCHAs:")
    logger.info(f"  Best epoch for 5px threshold: Epoch {real_best_5px_epoch} "
               f"(Both accuracy: {max(results['real_5px_both_accuracy']):.1f}%)")
    logger.info(f"  Best epoch for 7px threshold: Epoch {real_best_7px_epoch} "
               f"(Both accuracy: {max(results['real_7px_both_accuracy']):.1f}%)")
    logger.info("="*60)
    
    print(f"\nTraining analysis complete! Check the logs directory for results.")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Comprehensive Model Evaluation Tool')
    parser.add_argument('--mode', type=str, default='best',
                        choices=['best', 'training', 'all', 'compare'],
                        help='Evaluation mode: best (evaluate best model), '
                             'training (analyze training progress), '
                             'all (run both evaluations), '
                             'compare (compare multiple models)')
    parser.add_argument('--models', type=str, nargs='+', 
                        help='Specific model paths to evaluate (for compare mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'best' or args.mode == 'all':
        print("\n" + "="*60)
        print("EVALUATING BEST MODEL")
        print("="*60)
        evaluate_best_model()
    
    if args.mode == 'training' or args.mode == 'all':
        print("\n" + "="*60)
        print("ANALYZING TRAINING PROGRESS")
        print("="*60)
        analyze_training_progress()
    
    if args.mode == 'compare':
        print("\n" + "="*60)
        print("COMPARING MULTIPLE MODELS")
        print("="*60)
        if args.models:
            evaluate_best_model(args.models)
        else:
            # 自动查找所有best_model文件
            evaluate_best_model()
    
    print("\nEvaluation complete!")


if __name__ == "__main__":
    main()