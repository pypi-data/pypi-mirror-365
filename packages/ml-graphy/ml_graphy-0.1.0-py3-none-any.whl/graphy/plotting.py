import matplotlib.pyplot as plt
import seaborn as sns


def plot_metrics(mod):
    sns.set_style("darkgrid")
    sns.set_palette("muted")
    sns.set_context("notebook")
    
    has_val_loss = 'val_loss' in mod.history
    has_val_accuracy = 'val_accuracy' in mod.history
    has_loss = 'loss' in mod.history
    has_accuracy = 'accuracy' in mod.history
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle('Training Metrics', fontsize=16, fontweight='bold')
    
    if has_loss:
        axes[0].plot(mod.history['loss'], label='Training Loss', linewidth=2)
        if has_val_loss:
            axes[0].plot(mod.history['val_loss'], label='Validation Loss', linewidth=2)
            print("Plotting both training and validation loss")
        else:
            print("No validation loss found - plotting training loss only")
        
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Model Loss')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
    else:
        axes[0].text(0.5, 0.5, 'No loss data available', ha='center', va='center', transform=axes[0].transAxes)
        axes[0].set_title('Loss - No Data')
    
    if has_accuracy:
        axes[1].plot(mod.history['accuracy'], label='Training Accuracy', linewidth=2)
        if has_val_accuracy:
            axes[1].plot(mod.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
            print("Plotting both training and validation accuracy")
        else:
            print("No validation accuracy found - plotting training accuracy only")

        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title('Model Accuracy')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    else:
        axes[1].text(0.5, 0.5, 'No accuracy data available', ha='center', va='center', transform=axes[1].transAxes)
        axes[1].set_title('Accuracy - No Data')
    
    plt.tight_layout()
    plt.show()
    
    print(f">> Training Summary:")
    print(f"   - Total epochs: {len(mod.history.get('loss', []))}")
    print(f"   - Validation data: {'Yes' if has_val_loss or has_val_accuracy else 'No'}")
    if has_loss:
        print(f"   - Final training loss: {mod.history['loss'][-1]:.4f}")
    if has_val_loss:
        print(f"   - Final validation loss: {mod.history['val_loss'][-1]:.4f}")
    if has_accuracy:
        print(f"   - Final training accuracy: {mod.history['accuracy'][-1]:.4f}")
    if has_val_accuracy:
        print(f"   - Final validation accuracy: {mod.history['val_accuracy'][-1]:.4f}")
